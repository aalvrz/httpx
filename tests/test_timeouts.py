import pytest

import httpx


async def test_read_timeout(server, backend):
    timeout = httpx.Timeout(read_timeout=1e-6)

    async with httpx.Client(timeout=timeout) as client:
        with pytest.raises(httpx.ReadTimeout):
            await client.get(server.url.copy_with(path="/slow_response"))


async def test_write_timeout(server, backend):
    timeout = httpx.Timeout(write_timeout=1e-6)

    async with httpx.Client(timeout=timeout) as client:
        with pytest.raises(httpx.WriteTimeout):
            data = b"*" * 1024 * 1024 * 100
            await client.put(server.url.copy_with(path="/slow_response"), data=data)


async def test_connect_timeout(server, backend):
    timeout = httpx.Timeout(connect_timeout=1e-6)

    async with httpx.Client(timeout=timeout) as client:
        with pytest.raises(httpx.ConnectTimeout):
            # See https://stackoverflow.com/questions/100841/
            await client.get("http://10.255.255.1/")


async def test_pool_timeout(server, backend):
    pool_limits = httpx.PoolLimits(hard_limit=1)
    timeout = httpx.Timeout(pool_timeout=1e-4)

    async with httpx.Client(pool_limits=pool_limits, timeout=timeout) as client:
        async with client.stream("GET", server.url):
            with pytest.raises(httpx.PoolTimeout):
                await client.get("http://localhost:8000/")
