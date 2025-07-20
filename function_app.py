""" Azure Function to ping a list of URLs. """
import azure.functions as func
import logging
import os
import asyncio
import aiohttp

app = func.FunctionApp()


# noinspection PyUnusedLocal
@app.timer_trigger(schedule="0 */5 * * * *", arg_name="myTimer", run_on_startup=False)
async def url_pinger(myTimer: func.TimerRequest) -> None:
    """ Pings a list of URLs defined in the 'URLsToPing' environment variable. """
    logging.info('Python timer trigger function has started.')

    urls_to_ping_str = os.environ.get('URLS_TO_PING', '')

    if not urls_to_ping_str:
        logging.warning("The 'URLsToPing' application setting is not set. No URLs to ping.")
        return

    url_list = [url.strip() for url in urls_to_ping_str.split(',') if url.strip()]

    if not url_list:
        logging.warning("The 'URLsToPing' setting was present but contained no valid URLs.")
        return

    logging.info(f"Pinging {len(url_list)} URLs.")

    async with aiohttp.ClientSession() as session:
        ping_tasks = [ping_url_async(session, url) for url in url_list]
        await asyncio.gather(*ping_tasks)

    logging.info('Pinging task completed.')


async def ping_url_async(session: aiohttp.ClientSession, url: str) -> None:
    """ Sends a GET request to a single URL and logs the outcome. """
    try:
        async with session.get(url, timeout=30) as response:
            if 200 <= response.status < 300:
                logging.info(f"SUCCESS: {url} responded with status {response.status}")
            else:
                logging.warning(f"FAILURE: {url} responded with status {response.status}")
    except asyncio.TimeoutError:
        logging.error(f"ERROR: Pinging {url} failed with a timeout.")
    except Exception as e:
        logging.error(f"ERROR: Pinging {url} failed with an exception: {e}", exc_info=False)
