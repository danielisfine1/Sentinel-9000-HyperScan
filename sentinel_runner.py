import asyncio
import json
import time
import os
import requests
from playwright.async_api import async_playwright

TASKS_FILE = "sentinel_tasks.json"

def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, 'r') as f:
        return json.load(f)

def save_tasks(tasks):
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=2)

async def run_task(playwright, task):
    browser = await (playwright.chromium.launch(headless=(task['method'] == 'headless')))
    context = await browser.new_context()
    page = await context.new_page()

    logs = []
    network = []

    page.on("console", lambda msg: logs.append(msg.text()))
    page.on("request", lambda req: network.append(f"REQ {req.method} {req.url}"))
    page.on("response", lambda res: network.append(f"RES {res.status} {res.url}"))

    try:
        await page.goto(task['url'])
        await asyncio.sleep(task['sleep'])

        if not await page.query_selector(task['selector']):
            requests.post(task['webhook'], json={
                "status": "selector_not_found",
                "url": task['url'],
                "selector": task['selector'],
                "logs": logs,
                "network": network
            })
    except Exception as e:
        requests.post(task['webhook'], json={
            "status": "error",
            "url": task['url'],
            "error": str(e),
            "logs": logs,
            "network": network
        })
    finally:
        await browser.close()

async def main_loop():
    while True:
        tasks = load_tasks()
        now = time.time()
        updated = False

        async with async_playwright() as p:
            for task in tasks:
                if now - task['last_checked'] >= task['frequency']:
                    await run_task(p, task)
                    task['last_checked'] = now
                    updated = True

        if updated:
            save_tasks(tasks)

        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main_loop())
