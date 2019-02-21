<?php
# get parameter o
if(isset($_GET["o"]))
{
	$o=$_REQUEST["o"];
}
# append it to the file
$f=fopen("d:/d/forge2018/php_data.txt", "a");
fwrite($f,$o);
fclose($f);
?>