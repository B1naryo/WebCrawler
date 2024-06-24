import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import time
import argparse
import logging
from threading import Thread, Lock
from queue import Queue

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extrair_urls(url, page_content, domain):
    soup = BeautifulSoup(page_content, 'html.parser')
    urls = set()

    for link in soup.find_all('a'):
        href = link.get('href')
        if href:
            absolute_url = urljoin(url, href)
            parsed_url = urlparse(absolute_url)
            if parsed_url.netloc == domain:  # Verifica se o domínio é o mesmo da URL inicial
                urls.add(absolute_url)

    return urls

def worker(queue, urls_visitadas, lock, domain, max_profundidade):
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': ''
    }
    
    while True:
        url_atual, profundidade_atual = queue.get()
        if profundidade_atual > max_profundidade:
            queue.task_done()
            continue
        with lock:
            if url_atual in urls_visitadas:
                queue.task_done()
                continue
            urls_visitadas.add(url_atual)

        try:
            response = session.get(url_atual, headers=headers)
            response.raise_for_status()
            page_content = response.text

            urls_encontradas = extrair_urls(url_atual, page_content, domain)

            with lock:
                with open("urls_associadas.txt", "a") as file:
                    for link in urls_encontradas:
                        file.write(f"{link}\n")

            for nova_url in urls_encontradas:
                queue.put((nova_url, profundidade_atual + 1))

            time.sleep(1)

        except requests.exceptions.RequestException as e:
            logging.error(f"Erro ao acessar a URL {url_atual}: {e}")

        queue.task_done()

def crawl_paginas(url, max_profundidade=3, num_threads=4):
    urls_visitadas = set()
    queue = Queue()

    # Verifica se a URL tem um esquema (http:// ou https://), adiciona https:// se não tiver
    if not urlparse(url).scheme:
        url = "https://" + url

    queue.put((url, 0))
    parsed_url = urlparse(url)
    domain = parsed_url.netloc  # Extrai o domínio da URL inicial

    lock = Lock()

    # Inicializa e começa os workers
    for _ in range(num_threads):
        thread = Thread(target=worker, args=(queue, urls_visitadas, lock, domain, max_profundidade))
        thread.daemon = True
        thread.start()

    queue.join()

def main():
    parser = argparse.ArgumentParser(description="Web Crawler")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-d", "--domain", type=str, help="URL única para rastrear")
    group.add_argument("-f", "--file", type=str, help="Arquivo contendo URLs para rastrear")
    parser.add_argument("-p", "--profundidade", type=int, default=10, help="Profundidade máxima de rastreamento")
    parser.add_argument("-t", "--threads", type=int, default=4, help="Número de threads para rastreamento")

    args = parser.parse_args()

    if args.domain:
        crawl_paginas(args.domain, args.profundidade, args.threads)
    elif args.file:
        with open(args.file, "r") as file:
            urls = file.readlines()
            for url in urls:
                crawl_paginas(url.strip(), args.profundidade, args.threads)

if __name__ == "__main__":
    main()

