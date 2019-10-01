for foo in `ls *.dot`; do dot -Tpng $foo > $foo.png; done
