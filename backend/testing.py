import subprocess

filepath = "/Users/kanishk/Downloads"
fileData = subprocess.run(f"ls -i1p '{filepath}' | grep -v /", capture_output=True, text=True, shell=True).stdout.split('\n')
for(n) in range(len(fileData)):
    fileData[n]=fileData[n].lstrip()
    fileData[n]=fileData[n].split(' ')
fileData.remove([''])
# fileData = subprocess.run(f"ls -i1p '{filepath}'", capture_output=True, text=True, shell=True).stdout
# fileData = subprocess.run(["ls", "-i", filepath+filename], capture_output=True, text=True).stdout.split(' ')

# fileData=fileData.split(' ')

# fileData[1]=fileData[1].replace('\n','')
# inode = fileData[0]
# fileFromInode = subprocess.run(["find","/Users/rishinatraj/Documents","-inum" ,inode], capture_output=True, text=True).stdout.replace('\n','')
# if fileFromInode == "":
#     fileFromInode = "File not found"
    
# fileFromInode=fileFromInode.stdout
# fileFromInode=fileFromInode.replace('\n','')

print(fileData)
# print(fileFromInode)
