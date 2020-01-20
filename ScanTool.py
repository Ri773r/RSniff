import aiohttp
import aiofiles
import asyncio
import os
import time
import click
import json

UA = {
	"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"
}	

class Scan(object):
	def __init__(self, base_url, dict_path, headers, max_concurrency=10, timeout=2, queue_cap=50):
		self.q = asyncio.Queue(queue_cap)
		self.s = asyncio.Queue()
		self.max_concurrency = max_concurrency
		self.timeout = timeout
		self.base_url = base_url
		self.dict_path = dict_path
		self.headers = headers
		self.lines = 0

	def readFromFolder(self):
		files = os.listdir(self.dict_path)
		files = [os.path.join(self.dict_path, file) for file in files if file.endswith(".txt")]
		return files

	def urljoin(self, suffix):
		if suffix.startswith("/"):
			suffix = suffix[1:]
		return "{base_url}/{suffix}".format(base_url=self.base_url, suffix=suffix)

	async def fetch(self, session, url):
		async with session.head(url, timeout=self.timeout) as resp:
			return resp.status

	async def crawl(self, name):
		# each crawl has a session
		async with aiohttp.ClientSession(headers=self.headers) as session:
			while True:
				url = await self.q.get()
				url = self.urljoin(url)
				try:
					status = await self.fetch(session, url)
					if status == 200:
						print("Success ", url)
				except Exception as e:
					self.s.put_nowait(False)
				finally:
					# must call task_done or else block in join
					self.q.task_done()

	async def put(self):
		files = self.readFromFolder()
		for file in files:
			async with aiofiles.open(file, mode="r") as f: 
				print("File {}".format(os.path.split(file)[1]))
				async for line in f:
					self.lines += 1
					# delete character "\n"
					await self.q.put(line[:-1])
		print("Total scan lines ", self.lines)
		# print("Put Out!")

	async def run(self):
		crawls = [self.crawl(i) for i in range(self.max_concurrency)]
		consumer = asyncio.gather(*crawls)
		await self.put()
		await self.q.join()
		# cancel consumer
		consumer.cancel()
		print("Finish ")
		print("Timeout ", self.s.qsize())

	def loop(self):
		loop = asyncio.get_event_loop()
		loop.run_until_complete(self.run())
		loop.close()


def banner(base_url, dict_path, headers, max_concurrency, timeout, queue_cap):
	print('''
                 ___           ___           ___                       ___         ___   
                /  /\\         /  /\\         /__/\\        ___          /  /\\       /  /\\  
               /  /::\\       /  /:/_        \\  \\:\\      /  /\\        /  /:/_     /  /:/_ 
              /  /:/\\:\\     /  /:/ /\\        \\  \\:\\    /  /:/       /  /:/ /\\   /  /:/ /\\
             /  /:/~/:/    /  /:/ /::\\   _____\\__\\:\\  /__/::\\      /  /:/ /:/  /  /:/ /:/
            /__/:/ /:/___ /__/:/ /:/\\:\\ /__/::::::::\\ \\__\\/\\:\\__  /__/:/ /:/  /__/:/ /:/ 
            \\  \\:\\/:::::/ \\  \\:\\/:/~/:/ \\  \\:\\~~\\~~\\/    \\  \\:\\/\\ \\  \\:\\/:/   \\  \\:\\/:/  
             \\  \\::/~~~~   \\  \\::/ /:/   \\  \\:\\  ~~~      \\__\\::/  \\  \\::/     \\  \\::/   
              \\  \\:\\        \\__\\/ /:/     \\  \\:\\          /__/:/    \\  \\:\\      \\  \\:\\   
               \\  \\:\\         /__/:/       \\  \\:\\         \\__\\/      \\  \\:\\      \\  \\:\\  
                \\__\\/         \\__\\/         \\__\\/                     \\__\\/       \\__\\/  
		''')
	print("Base Url:", base_url)
	print("Dictionary Folder:", dict_path)
	print("Headers:", headers)
	print("Max Concurrency:", max_concurrency)
	print("Timeout:", timeout)
	print("Queue Capacity:", queue_cap)
	print("\n")


@click.command()
@click.option("--baseUrl", "-u", required=True, help="Basice URL of splicing")
@click.option("--dictPath", "-p", required=True, help="Dictionary path")
@click.option("--customerHeaders", "-h", default=json.dumps(UA), help="Customer headers")
@click.option("--maxConcurrency", "-c", default=10, show_default=True, help="Maximum concurrent")
@click.option("--timeout", "-t", default=2, show_default=True, help="Timeout time")
@click.option("--queueCap", "-q", default=50, show_default=True, help="Queeu capacity")
def scan(baseurl, dictpath, customerheaders, maxconcurrency, timeout, queuecap):
	'''
	Web background scanning tool based on Python coroutine
	'''
	headers = json.loads(customerheaders)
	banner(baseurl, dictpath, headers, maxconcurrency, timeout, queuecap)
	start = time.perf_counter()
	sc = Scan(baseurl, dictpath, headers, maxconcurrency, timeout, queuecap)
	sc.loop()
	print("Use time {}s".format(time.perf_counter() - start))


if __name__ == '__main__':
	scan()
