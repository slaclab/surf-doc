import web
#Python server to recieve github webhooks and parse the data
#runs script to create and push documentation for the project to github

urls = ('/.*', 'hooks')

app = web.application(urls, globals())

class hooks:
    def POST(self):
        data = web.data()

		try:
	        #check the incoming POST matches a github webhook
	        if data.get('repository') is not None:

				repo = data.get('repository')
				repo_path = data.get('ssh_url')

				name = repo.get('name')
				full_name = repo.get('full_name')
				owner = repo.get('owner')
				login = owner.get('login')
				doc_path = "git@github.com:{}/{}_documentation.git".format(login, name)

				if data.get('release') is not None:
					release = data.get('release')
					rel_id = release.get('id')

			        subprocess.call(['bash', '/Users/Steven/SLAC/surf/doc/automatically_publish_doxygen.sh', repo_path, doc_path, rel_id, name])

	        return 'OK'
		
		except TypeError:

	    	print "Post not valid webhook"

	    	return 'TypeError'


if __name__ == '__main__':
    app.run()
