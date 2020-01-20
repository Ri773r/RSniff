import aiohttp
import asyncio
import os
import time
import click

class Scan(object):
	def __init__(self, base_url, dict_path, max_concurrency=10, timeout=2, queue_cap=50):
		self.q = asyncio.Queue(queue_cap)
		self.s = asyncio.Queue()
		self.max_concurrency = max_concurrency
		self.timeout = timeout
		self.base_url = base_url
		self.dict_path = dict_path
		self.urls = []

	def readFromFolder(self):
		files = os.listdir(self.dict_path)
		files = [os.path.join(self.dict_path, file) for file in files if file.endswith(".txt")]
		return files

	def urljoin(self, suffix):
		if suffix.startswith("/"):
			suffix = suffix[1:]
		return "{base_url}/{suffix}".format(base_url=self.base_url, suffix=suffix)

	async def crawl(self, name):
		while True:
			url = await self.q.get()
			url = self.urljoin(url)
			try:
				async with aiohttp.ClientSession() as session:
					async with session.head(url, timeout=self.timeout) as resp:
						if resp.status == 200:
							print("Success ", url)
			except Exception as e:
				self.s.put_nowait(False)
			finally:
				# must call task_done or else block in join
				self.q.task_done()

	async def put(self):
		files = self.readFromFolder()
		for file in files:
			with open(file) as f:
				urls = f.read().split("\n")
			print("File {}, URL Count {}".format(os.path.split(file)[1], len(urls)))
			while len(urls) > 0:
				await self.q.put(urls.pop())
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


def banner(base_url, dict_path, max_concurrency, timeout, queue_cap):
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
	print("Max Concurrency:", max_concurrency)
	print("Timeout:", timeout)
	print("Queue Capacity:", queue_cap)
	print("\n")


@click.command()
@click.option("--baseUrl", "-u", required=True, help="Basice URL of splicing")
@click.option("--dictPath", "-p", required=True, help="Dictionary path")
@click.option("--maxConcurrency", "-c", default=10, show_default=True, help="Maximum concurrent")
@click.option("--timeout", "-t", default=2, show_default=True, help="Timeout time")
@click.option("--queueCap", "-q", default=50, show_default=True, help="Queeu capacity")
def scan(baseurl, dictpath, maxconcurrency, timeout, queuecap):
	'''
	Web background scanning tool based on Python coroutine
	'''
	banner(baseurl, dictpath, maxconcurrency, timeout, queuecap)
	start = time.perf_counter()
	sc = Scan(baseurl, dictpath, maxconcurrency, timeout, queuecap)
	sc.loop()
	print("Use time {}s".format(time.perf_counter() - start))

if __name__ == '__main__':
	scan()
	
