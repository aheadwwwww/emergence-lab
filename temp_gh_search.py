from github import Github

g = Github()
queries = ['cellular automata lenia', 'artificial life simulation', 'emergent behavior python', 'neural cellular automata']

results = []
for q in queries:
    repos = g.search_repositories(query=q, sort='stars', order='desc')
    for repo in list(repos)[:3]:
        results.append({
            'name': repo.full_name,
            'desc': (repo.description or 'N/A')[:100],
            'stars': repo.stargazers_count,
            'url': repo.html_url,
            'lang': repo.language or 'N/A'
        })

seen = set()
for r in sorted(results, key=lambda x: -x['stars']):
    if r['name'] not in seen:
        seen.add(r['name'])
        print(f'{r["name"]} ({r["stars"]}*) [{r["lang"]}]')
        print(f'{r["desc"]}')
        print(f'{r["url"]}')
        print()