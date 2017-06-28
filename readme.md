Depo
====

Depo is a very simple dependency manager for git projects. I developed it because
other solutions (I'm doing C++ development) always seemed extra heavy to me.

Command usage
-------------

The script must be fed with a json configuration file describing the dependencies
you need to download. An example configuration is presented below.

```
$ python depo.py -h
usage: depo.py [-h] [-v] [-u] [-c] [-i INPUT] [-o OUTPUT]


optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         verbose output
  -u, --update          update this script
  -c, --clear           clear dependencies folder before fetching
  -i INPUT, --input INPUT
                        path to the configuration file, default is
                        './deps.json'
  -o OUTPUT, --output OUTPUT
                        path to the dependencies installation folder, default
                        is './external'
```

Example configuration file
--------------------------

The package list is a plain list. Just add a new json object with :

- the name of the package ; it will define the folder in which the git package will be downloaded
- its origin, defined as a git address (https works fine, I don't know yet for ssh)
- the branch or version you need


```json
{
	"packages" :
	[
		{
			"name" : "fmt",
			"version" : "3.0.2",
			"origin" : "https://github.com/fmtlib/fmt.git"
		},
		{
			"name" : "lofx",
			"branch" : "master",
			"origin" : "https://github.com/brainsandwich/lofx.git"
		}
	]
}
```

Auto update
-----------

The script can be auto updated with newer versions. It sounds risky but I don't
want to do git management for a script that simple in my projects. With this feature
you just need to copy the python script once and update it once in a while ; and
check if the newer version is okay