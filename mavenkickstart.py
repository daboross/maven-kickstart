#!/usr/bin/env python3
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
import os
import re
import subprocess

from jinja2.environment import Template

__author__ = 'daboross'

# files to create
files = {
    "pom.xml": "pom.xml",
    "plugin.yml": "src/main/resources/plugin.yml",
    "plugin.java": "src/main/java/{src_dir}/{name}Plugin.java",
    "gitignore": ".gitignore",
}

template_dir = os.path.join(os.path.dirname(__file__), "templates")


def name_to_artifact(name):
    # For names like FirstSECONDThird
    name = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1-\2', name).lower()


class MavenKickstartCreator:
    """
    :type args: argparse.Namespace
    :type name: str
    :type desc: str
    :type github_name: str
    :type directory: str
    """

    def __init__(self):
        self.args = None
        self.name = None
        self.desc = None
        self.github_name = None
        self.directory = None

    def init_command_line(self):
        parser = argparse.ArgumentParser(description="Create maven projects with ease")
        # main properties
        parser.add_argument('--name', required=True,
                            help="Name of the project")
        parser.add_argument('--directory',
                            help="Directory to put the project in, defaulting to $PWD/$NAME")
        parser.add_argument('--desc',
                            help="Description of the project", metavar="DESCRIPTION")
        # maven properties
        parser.add_argument('--group', metavar="MAVEN_GROUP", dest="maven_group",
                            help="Maven groupId")
        parser.add_argument('--artifact', metavar="MAVEN_ARTIFACT", dest="maven_artifact",
                            help="Maven artifactId, defaulting to project name, replacing capatalization with dashes")
        # github properties
        parser.add_argument('--github', metavar="REPO_NAME",
                            help="Name of github repository to create")
        parser.add_argument('--github-organization', metavar="ORG_NAME", default="daboross", dest="github_org",
                            help="Name of the github organization to create a repository under")

        # plugin toggle properties
        parser.add_argument('--metrics', dest='metrics', action='store_true', default=True,
                            help="Enables metrics in the plugin, enabled by default")
        parser.add_argument('--no-metrics', dest='metrics', action='store_false',
                            help="Disables metrics in the plugin")
        parser.add_argument('--distribute', dest='add_distribution', action='store_true', default=True,
                            help="Enables  distribution via maven repository for the plugin, disabled by default")
        parser.add_argument('--no-distribute', dest='add_distribution', action='store_false',
                            help="Disables distribution via maven repository for the plugin")

        # author properties
        parser.add_argument('--author', default="Dabo Ross", dest="author_name",
                            help="Full name of author")
        parser.add_argument('--author-email', default="daboross@daboross.net", dest="author_email",
                            help="Email address of the author")
        parser.add_argument('--author-website', default="http://daboross.net", dest="author_website",
                            help="Website address of the author")

        args = parser.parse_args()

        if args.directory is None:
            args.directory = os.path.abspath(os.path.join(os.path.curdir, args.name))
        else:
            args.directory = os.path.abspath(args.directory)

        if args.desc is None:
            args.desc = args.name

        if args.maven_artifact is None:
            args.maven_artifact = name_to_artifact(args.name)

        if args.maven_group is None:
            args.maven_group = "net.daboross.bukkitdev.{}".format(args.maven_artifact)

        args.java_package = args.maven_group.replace("-", "")
        args.src_dir = args.java_package.replace(".", os.path.sep)
        args.author_id = args.author_name.lower().replace(" ", "")

        self.args = args
        self.name = args.name
        self.desc = args.desc
        self.directory = args.directory
        self.github_name = args.github

    def generate(self):
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

        self.init_github()
        if self.github_name:
            self.create_github_repo()

    def init_github(self):
        subprocess.call(["git", "init"], cwd=self.directory)

    def create_github_repo(self):
        pass


if __name__ == "__main__":
    creator = MavenKickstartCreator()
    creator.init_command_line()
    creator.generate()