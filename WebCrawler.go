package main

import (
	"bufio"
	"flag"
	"fmt"
	"log"
	"net/http"
	"net/url"
	"os"
	"strings"
	"sync"

	"github.com/PuerkitoBio/goquery"
)

// Set to keep track of visited URLs
var visited = struct {
	m map[string]bool
	sync.Mutex
}{m: make(map[string]bool)}

func main() {
	urlFlag := flag.String("d", "", "URL para iniciar o rastreamento")
	fileFlag := flag.String("f", "", "Arquivo contendo URLs para iniciar o rastreamento")
	depthFlag := flag.Int("depth", 1, "Profundidade máxima para rastrear")

	flag.Parse()

	var startURLs []string
	if *urlFlag != "" {
		startURLs = append(startURLs, *urlFlag)
	} else if *fileFlag != "" {
		file, err := os.Open(*fileFlag)
		if err != nil {
			log.Fatalf("Erro ao abrir o arquivo: %v", err)
		}
		defer file.Close()

		scanner := bufio.NewScanner(file)
		for scanner.Scan() {
			startURLs = append(startURLs, scanner.Text())
		}
		if err := scanner.Err(); err != nil {
			log.Fatalf("Erro ao ler o arquivo: %v", err)
		}
	} else {
		log.Fatal("Você deve fornecer uma URL com -d ou um arquivo com -f")
	}

	results := startCrawl(startURLs, *depthFlag)
	for _, result := range results {
		fmt.Println(result)
	}
}

func startCrawl(startURLs []string, maxDepth int) []string {
	var wg sync.WaitGroup
	var mu sync.Mutex
	results := []string{}

	var crawl func(string, int, string)
	crawl = func(u string, depth int, domain string) {
		defer wg.Done()
		if depth > maxDepth {
			return
		}

		visited.Lock()
		if visited.m[u] {
			visited.Unlock()
			return
		}
		visited.m[u] = true
		visited.Unlock()

		res, err := http.Get(u)
		if err != nil {
			log.Println("Erro ao buscar:", u, err)
			return
		}
		defer res.Body.Close()

		if res.StatusCode != 200 {
			log.Println("Status HTTP não OK:", res.StatusCode)
			return
		}

		doc, err := goquery.NewDocumentFromReader(res.Body)
		if err != nil {
			log.Println("Erro ao analisar HTML:", err)
			return
		}

		mu.Lock()
		results = append(results, u)
		mu.Unlock()

		doc.Find("a[href]").Each(func(i int, s *goquery.Selection) {
			link, exists := s.Attr("href")
			if !exists {
				return
			}

			link = resolveURL(u, link)
			if isSameDomain(link, domain) {
				wg.Add(1)
				go crawl(link, depth+1, domain)
			}
		})
	}

	for _, startURL := range startURLs {
		domain := getDomain(startURL)
		wg.Add(1)
		go crawl(startURL, 0, domain)
	}
	wg.Wait()

	return results
}

func resolveURL(base, ref string) string {
	u, err := url.Parse(ref)
	if err != nil {
		return ""
	}
	baseURL, err := url.Parse(base)
	if err != nil {
		return ""
	}
	return baseURL.ResolveReference(u).String()
}

func getDomain(link string) string {
	u, err := url.Parse(link)
	if err != nil {
		return ""
	}
	return u.Host
}

func isSameDomain(link, domain string) bool {
	u, err := url.Parse(link)
	if err != nil {
		return false
	}
	return u.Host == domain
}
