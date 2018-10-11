# Employee Catalog Project
## About
This application provides a list of Companies as well as provide a user registration and authentication system. Registered users will have the ability to add, edit, and delete their own company and add, delete and edit employees of respected company. Non register user can view the company and companies employees.

## Features
Proper authentication and authorisation check. Full CRUD support using SQLAlchemy and Flask. JSON endpoints. Implements oAuth using Google Sign-in API.

## Project Structure
 ├── project.py:-Main file to run the project ├── client_secrets.json ├── fb_client_secrets.json ├── database_setup.py:-database file ├── add_employee.py ├── company.db ├── README.md ├── static | |__css | | |__styles.css │ └── img | |__blank_user.gif | |__top-banner.jpg | └── templates ├── company.html ├── deleteCompany.html ├── deleteemployee.html ├── editCompany.html ├── editemployee.html ├── employee.html ├── login.html ├── main.html ├── headers.html ├── publicCompany.html └── publicemployee.html |__newCompany.html |__newemployee.html

## Steps to run this project

>1.Install the VM and Vagrant: This project uses a virtual machine (VM) to run a project.

>2.If you don't already have virtual box on your machine, you can download it here: https://www.virtualbox.org/wiki/DownloadOldBuilds51 or for ubuntu type this command: sudo apt-get install virtual box

>3.Download and install Vagrant (if you do not already have it installed). This is the software that configures the VM and allows the host (your machine) to talk to the VM: https://www.vagrantup.com/ or for ubuntu type this commnad: sudo apt-get install vagrant ->you should be able to run vagrant --version after installation to see the version that was installed.

>4.Download and unzip this file:https://s3.amazonaws.com/video.udacity-data.com/topher/2018/April/5acfbfa3_fsnd-virtual-machine/fsnd-virtual-machine.zip This will give you a directory called FSND-Virtual-Machine. It may be located inside your Downloads folder.

>Alternately, you can use Github to fork and clone the repository https://github.com/udacity/fullstack-nanodegree-vm.

>5.cd into this(FSND_Virtual_Machine) directory

>6.cd into the vagrant/ subdirectory

>7.Bring the VM up with the command vagrant up

>8.Log into the VM with vagrant ssh

## How to run this project

1.Download or Clone this repository to your local drive:
https://github.com/mvcman/My-Item-Catalog-Employee

2.Copy this My-Item-Catalog-Employee into the FSND_Virtual_Machine/vagrant directory.

3.Open a terminal window from the FSND_Virtual_Machine/vagrant directory, or simply open a terminal window and cd into that directory.

4.Run vagrant ssh at the prompt to log in to the VM.
```
vagrant ssh
```

5.cd into the vagrant subdirectory
```
cd /vagrant
```
6.cd into the clone directory

7.Run the following command to set up the database:
```
python database_setup.py
```
8.Run the following command to insert items into your database. If you don't run this, the application will not show any item
```
python add_employee.py
```
9.Run this application:
```
python project.py
```
Open http://localhost:5000/ in your favourite Web browser, and enjoy.
