Depo
====

Depo is a very simple command line dependency manager for git/cmake projects. I developed it because
other solutions always seemed extra heavy to me (I'm doing C++ development).

It downloads and can build dependencies according to a JSON configuration file (example
given below).

Note on Build
-------------

The dependencies that are built need :

- to provide a CMakeLists.txt file
- to provide an INSTALL target (tested with Visual Studio ; I don't know for other generators ...)

Then, to use your freshly baked dependencies, you can use outputs in your cmake configuration :

```cmake
	find_library(SOMELIB_LIB somelib NAMES somelib3 somelib2 HINTS ${PROJECT_SOURCE_DIR}/external/lib)
	target_include_directories(target PUBLIC ${PROJECT_SOURCE_DIR}/external/include)
	target_link_libraries(target PUBLIC ${SOMELIB_LIB})
```

I've not tried with shared/dynamic libraries because it's always a mess on windows, and I'm not
doing anything regarding architecture (i.e. having subfolders for x86/x64/ARM/... libs)

Command usage
-------------

```
$ python depo.py -h
usage: depo.py [-h] [-v] [-u] [-c] [-f] [-b] [-i INPUT]

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         verbose output
  -u, --update          update this script
  -c, --clear           clear dependencies folder before fetching
  -f, --force           forces redownload of packages
  -b, --build           build packages
  -i INPUT, --input INPUT
                        path to the configuration file, default is
                        './deps.json'
```

Example configuration file
--------------------------

Generic configuration parameters :

- `download-path` : set the directory to download sources to (default is external/sources)
- `build-path` : set the directory in which to build sources (default is external/build)
- `output-path` : set the directory in which built files will be generated (default is external/output)
- `generator` : the CMake generator to use when building (use cmake --help to get a list of available generators on your platform)

The package list is a plain list. Just add a new json object with :

- `name` : name of the package ; it will define the folder in which the git package will be downloaded
- `origin` : git origin, defined as a git address (https works fine, I don't know yet for ssh)
- `branch` / `version`  : the branch or version you want to checkout
- `build` : does the package need to be built ?
- `build-options` : a list of CMake configuration options (`cmake ... -D<OPTION>`)

```json
{
	"download-path" : "external/sources",
	"build-path" : "external/build",
	"output-path" : "external/output",
	"generator" : "Visual Studio 15 2017 Win64",
	"packages" :
	[
		{
			"name" : "glfw",
			"version" : "3.2.1",
			"origin" : "https://github.com/glfw/glfw.git",
			"build" : true,
			"build-options" : [
				"GLFW_BUILD_DOCS=OFF",
				"GLFW_BUILD_EXAMPLES=OFF",
				"GLFW_BUILD_TESTS=OFF"
			]
		},
		{
			"name" : "gl3w",
			"branch" : "master",
			"origin" : "https://github.com/skaslev/gl3w.git",
			"build" : false
		}
	]
}
```

Auto update
-----------

The script can be auto updated with newer versions. It sounds risky but I don't
want to do git management for a script that simple in my projects. With this feature
you just need to copy the python script once and update it once in a while (`py depo.py -u`)
and check if the newer version is okay