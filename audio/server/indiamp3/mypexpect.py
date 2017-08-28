#!/usr/bin/python
#coding:utf-8

'''
该模块主要是利用pexpect模块，执行一些需要交互的shell简单命令；报错ssh和scp等
主要用于项目中需要远程传输文件时，创建不存在文件夹后上传
'''

import sys
import pexpect

class MyPexpect():
	
#    When you use this class,you must be want to control the same remote server
#    So you can provide the user,ip,passwd if you initialize it

	def __init__(self,user,ip,passwd):
		self.user = user
		self.ip =  ip
		self.passwd = passwd

	def F_ssh(self,command):

		sshPrompt = '#'
		ssh_newkey = "Are you sure you want to continue connecting"
		permission = "Permission denied, please try again."
		child = pexpect.spawn('ssh %s@%s' % (self.user,self.ip))
#		child.logfile_read = sys.stdout                #We can debug by this

		i = child.expect([pexpect.TIMEOUT,ssh_newkey,'password'])

		if i == 0: #Timeout
			print 'SSH could not login.Here is what SSH said:'
			print child.before,child.after
			raise ValueError
			return None
		
		elif i == 1: #First connect remote server
			child.sendline('yes')
			child.expect('password:')
			child.sendline(self.passwd)

		else:
#			child.expect("password:")
			child.sendline(self.passwd)

		child.expect(sshPrompt)
		child.sendline(command)

#child.expect(pexpect.EOF)    程序没有自动退出，期待到timeout；异常退出

		child.expect(sshPrompt)
		child.sendline('exit')
		child.expect(pexpect.EOF)

		print "SSH Command Finish"

		return child


#如果一个函数的某个参数是默认参数，则其后面的参数也必须是默认参
#def F_scp(user='root',ip='85.25.46.133',passwd='tv11Mar2015',src,dest):
	def F_scp(self,src,dest):

		cmd = ('scp %s %s@%s:"%s" '  % (src,self.user,self.ip,dest))
#		print cmd 
		child = pexpect.spawn('scp %s %s@%s:"%s" '  % (src,self.user,self.ip,dest))
		child.logfile_read = sys.stdout

		child.expect('password')
		child.sendline(self.passwd)

		child.expect(pexpect.EOF)
		print "Scp Command Finish"


def test():
	mp = MyPexpect('root','85.25.46.133','tv11Mar2015')
	try:
		mp.F_ssh('mkdir -p /root/This\ is\ Test/wang\ \(2015\)')
	except ValueError:
		print 'jlsfl'
	mp.F_scp(src='1.mp3',dest='/root/This\ is\ Test/wang\ \(2015\)/scp.mp3')

if __name__ == '__main__':
	test()
