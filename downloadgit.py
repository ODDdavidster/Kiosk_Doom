#!/usr/bin/env python3

"""
This script downloads all the assets for one or more releases of a given GitHub
repository in parallel; see the --help output for details.  It serves as an
example of asynchronous programming in Python, written to accompany the article
<https://jwodder.github.io/kbits/posts/pyasync-fundam/>.
Requirements: Python 3.8+, the ghrepo and httpx packages
"""

# The MIT License (MIT)
#
# Copyright (c) 2022 John Thorvald Wodder II
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import annotations

__requires__ = ["ghrepo", "httpx"]
import argparse
import asyncio
from collections.abc import AsyncIterable, AsyncIterator
from dataclasses import dataclass
import json
import os
from pathlib import Path
import logging
import sys
from textwrap import indent
from typing import Optional, TypeVar
from ghrepo import GHRepo
import httpx

T = TypeVar("T")

log = logging.getLogger()


@dataclass
class AssetDownloader:
    """
    A client for asynchronously downloading release assets of a given
    GitHub repository
    """

    #: The httpx client object
    client: httpx.AsyncClient
    #: The parsed owner & name of the repository we're downloading from
    repo: GHRepo
    #: The root directory in which to save release assets.  The assets for a
    #: given release will all be placed in a subdirectory named after the
    #: release's tag.
    download_dir: Path

    async def get_release(self, tag: str) -> Optional[Release]:
        """
        Fetch the details for the release with the given tag from the API.  If
        there is no such release, returns `None`.
        """
        log.info("Fetching details on release %s", tag)
        r = await self.client.get(f"{self.repo.api_url}/releases/tags/{tag}")
        if r.status_code == 404:
            log.warning("%s: no such release", tag)
            return None
        r.raise_for_status()
        return Release.from_payload(r.json())

    async def get_many_releases(self, tags: list[str]) -> AsyncIterator[Release]:
        """
        Returns an iterator of `Release` objects for the given tags.  Tags
        which do not correspond to an extant release are discarded.  If an
        error occurs, pending retrievals are cancelled, and the error is
        reraised.
        """
        tasks = [asyncio.create_task(self.get_release(t)) for t in tags]
        async for rel in aiter_until_error(tasks):
            if rel is not None:
                yield rel

    async def get_all_releases(self) -> AsyncIterator[Release]:
        """Paginate through the repository's releases and yield each one"""
        log.info("Fetching all releases for %s", self.repo)
        url: Optional[str] = f"{self.repo.api_url}/releases"
        while url is not None:
            r = await self.client.get(url)
            r.raise_for_status()
            for obj in r.json():
                yield Release.from_payload(obj)
            url = r.links.get("next", {}).get("url")

    async def download_release_assets(
        self, releaseiter: AsyncIterable[Release]
    ) -> bool:
        """
        Download the assets for the given releases.  Returns `True` iff all
        downloads completed successfully.
        If an HTTP error occurs while iterating over ``releaseiter``, it is
        logged and the method returns `False` without downloading anything.
        Non-HTTP errors propagate out.
        If an unexpected error occurs while downloading some file, all
        remaining downloads are cancelled.
        """
        releases: list[Release] = []
        # If an error occurs while fetching releases, it will propagate out
        # through the `async for` line here.  Hence, we wait until after all
        # releases have been fetched before calling create_task().
        try:
            async for rel in releaseiter:
                if rel.assets:
                    log.info(
                        "Found release %s with assets: %s",
                        rel.tag_name,
                        ", ".join(asset.name for asset in rel.assets),
                    )
                    releases.append(rel)
                else:
                    log.info("Release %s has no assets", rel.tag_name)
        except httpx.HTTPStatusError as e:
            log_http_error(e.response)
            return False
        except httpx.RequestError as e:
            log.error(
                "Error requesting %s: %s: %s", e.request.url, type(e).__name__, str(e)
            )
            return False
        tasks = [
            asyncio.create_task(self.download_asset(rel, asset))
            for rel in releases
            for asset in rel.assets
        ]
        if not tasks:
            log.info("No assets to download")
            return True
        downloaded = 0
        failed = 0
        async for ok in aiter_until_error(tasks):
            if ok:
                downloaded += 1
            else:
                failed += 1
        log.info(
            "%d assets downloaded successfully, %d downloads failed",
            downloaded,
            failed,
        )
        return not failed

    async def download_asset(self, release: Release, asset: Asset) -> bool:
        """
        Download the given asset belonging to the given release.  Returns
        `True` iff the download is successful.
        If an error occurs (or the task is cancelled), the download file is
        deleted.
        """
        target = self.download_dir / release.tag_name / asset.name
        log.info("%s: Downloading %s to %s", release.tag_name, asset.name, target)
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            log.error(
                "Error creating %s: %s: %s", target.parent, type(e).__name__, str(e)
            )
            return False
        try:
            async with self.client.stream("GET", asset.download_url) as r:
                if not r.is_success:
                    # Read the response body so it'll be available to
                    # r.json()/r.text:
                    await r.aread()
                    log_http_error(r)
                    return False
                downloaded = 0
                try:
                    with target.open("wb") as fp:
                        async for chunk in r.aiter_bytes():
                            fp.write(chunk)
                            downloaded += len(chunk)
                            log.info(
                                "%s: %s: downloaded %d / %d bytes (%.2f%%)",
                                release.tag_name,
                                asset.name,
                                downloaded,
                                asset.size,
                                downloaded / asset.size * 100,
                            )
                except OSError as e:
                    log.error(
                        "Error writing to %s: %s: %s", target, type(e).__name__, str(e)
                    )
                    target.unlink(missing_ok=True)
                    return False
                else:
                    log.info("%s: %s saved to %s", release.tag_name, asset.name, target)
                    return True
        except BaseException:
            target.unlink(missing_ok=True)
            raise


@dataclass
class Release:
    """A release of a GitHub repository"""

    # The actual API returns more fields than this, but these are the only ones
    # we're interested in.
    tag_name: str
    assets: list[Asset]

    @classmethod
    def from_payload(cls, data: dict) -> Release:
        """
        Construct a `Release` instance from a dict of release data returned by
        the GitHub REST API
        """
        return cls(
            tag_name=data["tag_name"],
            assets=[Asset.from_payload(a) for a in data["assets"]],
        )


@dataclass
class Asset:
    """An asset of a GitHub release"""

    # The actual API returns more fields than this, but these are the only ones
    # we're interested in.
    name: str
    download_url: str
    size: int

    @classmethod
    def from_payload(cls, data: dict) -> Asset:
        """
        Construct an `Asset` instance from a dict of asset data returned by the
        GitHub REST API
        """
        return cls(
            name=data["name"],
            download_url=data["browser_download_url"],
            size=data["size"],
        )


def main():
    logging.basicConfig(
        format="[%(levelname)-8s] %(message)s",
        level=logging.INFO,
    )
    parser = argparse.ArgumentParser(
        description=(
            "Download the release assets for the given tags of the given GitHub"
            " repository"
        )
    )
    parser.add_argument(
        "-A", "--all", action="store_true", help="Download assets for all releases"
    )
    parser.add_argument(
        "-d",
        "--download-dir",
        type=Path,
        metavar="PATH",
        default=os.curdir,
        help="Directory in which to download assets [default: current directory]",
    )
    parser.add_argument(
        "repo",
        type=GHRepo.parse,
        help=(
            "The GitHub repository from which to download assets.  Can be"
            " specified as either OWNER/NAME or https://github.com/OWNER/NAME."
        ),
    )
    parser.add_argument(
        "tags",
        nargs="*",
        help=(
            "The tags of the releases to download.  At least one tag or the"
            " --all option must be specified."
        ),
    )
    args = parser.parse_args()
    if not args.tags and not args.all:
        sys.exit("No tags specified on command line")
    if not asyncio.run(
        amain(
            repo=args.repo,
            tags=args.tags,
            download_dir=args.download_dir,
            all_releases=args.all,
        )
    ):
        sys.exit(1)


async def amain(
    repo: GHRepo, tags: list[str], download_dir: Path, all_releases: bool = False
) -> bool:
    async with httpx.AsyncClient(follow_redirects=True) as client:
        downloader = AssetDownloader(
            client=client, repo=repo, download_dir=download_dir
        )
        if all_releases:
            releases = downloader.get_all_releases()
        else:
            releases = downloader.get_many_releases(tags)
        return await downloader.download_release_assets(releases)


async def aiter_until_error(tasks: list[asyncio.Task[T]]) -> AsyncIterator[T]:
    """
    Given a list of tasks, yield their results as they become available.  If a
    task raises an error, all further tasks are cancelled, and the error is
    reraised.
    """
    for coro in asyncio.as_completed(tasks):
        try:
            value = await coro
        except BaseException:
            # Cancel all pending tasks (Calling cancel() on a task that's
            # already completed does nothing)
            for t in tasks:
                t.cancel()
            # Now we need to await for the cancels to take effect:
            await asyncio.wait(tasks)
            raise
        else:
            yield value


def log_http_error(r: httpx.Response) -> None:
    """
    Log an HTTP response that returned 4xx or 5xx.  If the body of the response
    is JSON, pretty-print it; otherwise, dump the body as-is.  (The body is
    indented underneath the log message either way.)
    """
    try:
        data = r.json()
    except ValueError:
        text = r.text
    else:
        text = json.dumps(data, indent=4)
    log.error(
        "Request to %s returned %d: %s\n\n%s\n",
        r.url,
        r.status_code,
        r.reason_phrase,
        indent(text, " " * 4),
    )


if __name__ == "__main__":
    main()