## install

dnf install -y gdb || yum install -y gdb

## 設定チェック

gdb -p 1 -batch -ex 'detach' 2>&1 | head -1
Attaching to process 1 的に進めばOK

Operation not permitted / ptrace: Function not permitted が出たら SYS_PTRACE or seccomp が不足

## 実行
gdb -p 1 -batch \
  -ex 'set pagination off' \
  -ex 'call (void*)freopen("/tmp/malloc_info.xml","w",stdout)' \
  -ex 'call (int)malloc_info(0, stdout)' \
  -ex 'call (int)fflush(stdout)'
