
python3 setup.py build_ext --inplace
mv exchange_lib.cpython-36m-x86_64-linux-gnu.so exchange_lib.so

git add -A
git commit -m "."
git push origin master
