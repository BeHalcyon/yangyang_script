

cd /root/project/yangyang_script

python3 setup.py build_ext --inplace

date ; read -t 10 -p "Hit ENTER or wait ten seconds" ; date

mv ./exchange_lib.cpython-36m-x86_64-linux-gnu.so ./exchange_lib.so

cd /root/project/yangyang_script

git add -A
git commit -m "."
git push origin master

rm exchange_lib.so
