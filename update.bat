@echo off
del v1.zip
"C:\Program Files\7-Zip\7z.exe" a "v1.zip" ".\*" -xr!.git -xr!logs
scp v1.zip root@v2202311209121242520.luckysrv.de:/root/
ssh root@v2202311209121242520.luckysrv.de './update_dev.sh'


