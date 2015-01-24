#!/usr/bin/perl -w
# rename - Larry's filename fixer
#用法: Perl表达式 [要处理的文件名]
$op = shift or die "Usage: 
rename expr [files]\n";
#如果没有给出要处理的文件名则从标准输入读入
chomp(@ARGV = <STDIN>) unless @ARGV; 
for (@ARGV) {
    $was = $_;
    eval $op; #对待处理的文件名($_)执行用户输入的Perl表达式$op
    die $@ if $@; #退出 , 如果eval出错
    rename($was,$_) unless $was eq $_;
}
#rename.perl  's/gongxu/leibie/g'  *    //将目录中所有文件名中的 gongxu 替换为 leibie。
#rename.perl 's/\.orig$//' *.orig #移除文件末尾的.orig
#rename.perl \"tr/A-Z/a-z/ unless /^Make/\" * #所有非Make打头的文件名大写转为小写
#rename.perl '$_ .= \".bad\"' *.f #每个*.f文件后面追加一个.bad
#rename.perl 'print \"$_: \"; s/foo/bar/ if <STDIN> =~ /^y/i' * #回显每个待处理的文件名, 等待输入, 如果用户输入以y或Y打头, 把文件名中的foo替换成bar
# find /tmp -name "*~" -print | rename.perl 's/^(.+)~$/.#$1/' #把 /tmp目录里面每个文件名末尾有~的文件名改成以.#开头
