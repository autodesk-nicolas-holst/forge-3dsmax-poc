<?php
$uuid=$_REQUEST["uuid"];
$t=file("d:/d/forge2018/php_data.txt");
$d="\n";
$a=Array();

echo "\n";

foreach($t as $line)
{
	if (substr($line,0,32)==$uuid)
	{
		if (substr($line,strlen($line)-5,4)=="|new")
		{
			$a[substr($line,33,15)]=substr($line,48+1,strlen($line)-4-48-2);
			#echo "add=".substr($line,48+1,strlen($line)-4-48-2)."\n";
		}
		if (substr($line,strlen($line)-9,8)=="|deleted")
		{
			$a[substr($line,33,15)]="";
			#echo "del=".substr($line,48+1,strlen($line)-4-48-2)."\n";
		}
		
	}
}

foreach($a as $key=>$line2)
{
	if (($line2!="")and($key!=""))
	{
		echo " ".$key." ".$line2."\n";
	}
}



?>