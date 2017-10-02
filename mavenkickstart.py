#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK
#
# Copyright 2014 Dabo Ross <http://www.daboross.net/>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import argparse
import codecs
import json
import os
import re
import subprocess

import argcomplete
from jinja2.environment import Template

__author__ = 'daboross'

# files to create
files = {
    "pom.xml": "pom.xml",
    "test.java": "src/test/java/JunitTests.java"
}

directories = [
    "src/main/java"
]

template_dir = os.path.join(os.path.dirname(__file__), "templates")


def name_to_artifact(name):
    # For names like FirstSECONDThird
    name = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1-\2', name).lower()


def add_togglable_property(parser, name, *, dest=None, default, help_content):
    """
    Adds a toggleable property to parser, with a --{name} option, and a --no-{name} option
    :type parser: argparse.ArgumentParser
    :type name: str
    :type default: bool
    :type help_content: str
    """
    if dest is None:
        dest = name.replace('-', '_')
    parser.add_argument('--{}'.format(name), dest=dest, action='store_true', default=default,
                        help="Enables {}. {} by default.".format(help_content, "Enabled" if default else "Disabled"))
    if default:
        # We don't need a --no-{name} option if it's disabled by default.
        parser.add_argument('--no-{}'.format(name), dest=dest, action='store_false', default=(not default),
                            help="Disables {}".format(help_content))


class MavenKickstartCreator:
    """
    :type name: str
    :type desc: str
    :type directory: str
    """

    def __init__(self):
        self.args = None
        self.name = None
        self.desc = None
        self.directory = None

    def init_command_line(self):
        parser = argparse.ArgumentParser(description="Create maven projects with ease", add_help=False)
        parser.add_argument("--help", action="help", help="show this help message and exit")  # to remove -h

        # main properties
        parser.add_argument('--name',
                            help="Name of the project")
        parser.add_argument('--directory',
                            help="Directory to put the project in, defaulting to $PWD/$NAME")
        parser.add_argument('--desc',
                            help="Description of the project", metavar="DESCRIPTION")
        add_togglable_property(parser, 'binary', dest="binary", default=True,
                            help_content="generate a plugin.yml and onEnable in the plugin.java")
        # maven properties
        parser.add_argument('--group', metavar="MAVEN_GROUP", dest="maven_group",
                            help="Maven groupId")
        parser.add_argument('--artifact', metavar="MAVEN_ARTIFACT", dest="maven_artifact",
                            help="Maven artifactId, defaulting to project name, replacing capatalization with dashes")

        # author properties
        parser.add_argument('--author', default="David Ross", dest="author_name",
                            help="Full name of author")
        parser.add_argument('--author-email', default="daboross@daboross.net", dest="author_email",
                            help="Email address of the author")
        parser.add_argument('--author-website', default="http://daboross.net", dest="author_website",
                            help="Website address of the author")
        parser.add_argument('--no-author', default=False, dest="add_author_info",
                            help="Disables adding author info", action="store_false")
        parser.add_argument('--no-license', default=True, dest="add_license", action="store_false",
                            help="Disables adding license info")

        argcomplete.autocomplete(parser)
        args = parser.parse_args()
        self.args = args

        if args.directory is None:
            if args.name is not None:
                args.directory = os.path.abspath(os.path.join(os.path.curdir, args.name))
        else:
            args.directory = os.path.abspath(args.directory)

        if args.name is None:
            return  # We won't do any other processing if the name isn't provided

        if args.name.islower():
            args.name = args.name.title()

        if args.desc is None:
            args.desc = args.name

        if args.maven_artifact is None:
            args.maven_artifact = name_to_artifact(args.name)

        if args.maven_group is None:
            args.maven_group = "net.daboross.school.{}".format(args.maven_artifact)

        args.java_package = args.maven_group.replace("-", "")
        args.src_dir = args.java_package.replace(".", os.path.sep)
        args.author_id = args.author_name.lower().replace(" ", "")

        self.name = args.name
        self.desc = args.desc
        self.directory = args.directory

    def generate(self):
        if self.args.name is not None:
            args = self.args.__dict__
            for template_name, file_path in files.items():
                file_path = file_path.format(**args)
                file_path = os.path.abspath(os.path.join(self.directory, file_path))

                file_dir = os.path.dirname(file_path)
                if not os.path.exists(file_dir):
                    print("Creating directory {}".format(file_dir))
                    os.makedirs(file_dir)
                print("Creating {}".format(file_path))

                with codecs.open(os.path.join(template_dir, template_name), encoding="utf-8") as stream:
                    text = stream.read()
                    newline = text.endswith("\n")  # fix for jinja2 templates removing trailing newline
                    template = Template(text)

                with codecs.open(file_path, "w", encoding="utf-8") as stream:
                    stream.write(template.render(**args))
                    if newline:
                        stream.write("\n")
            for directory_path in directories:
                directory_path = os.path.abspath(os.path.join(self.directory, directory_path))
                if not os.path.exists(directory_path):
                    print("Creating directory {}".format(directory_path))
                    os.makedirs(directory_path)


if __name__ == "__main__":
    creator = MavenKickstartCreator()
    creator.init_command_line()
    creator.generate()
