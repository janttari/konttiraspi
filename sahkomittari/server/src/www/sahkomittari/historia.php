<?php
$id=$_GET["id"];
echo "<a href='index.php'>[palaa]</a><br>";
echo "Historia asiakkaalle: ".$id. "<br><br><pre>";
echo "<pre>";
echo "aikaleima;id;kwh;pulssit;tuntikohtainen;lampo;kosteus;ulkolampo;ulkokosteus;\n";
        $db_kulutus = new SQLite3('/opt/konttiraspi/sahkomittari-server/data/kulutus.db');
        $sql = "SELECT * from kulutus WHERE id='".$id."' ORDER BY aikaleima";
        $kys_kulutus = $db_kulutus->query($sql);
        while($ret_kulutus = $kys_kulutus->fetchArray(SQLITE3_ASSOC)) {
               echo $ret_kulutus['aikaleima'] . ";" . $ret_kulutus['id'] . ";" . $ret_kulutus['kwh'] . ";" . $ret_kulutus['pulssit'] . ";" . $ret_kulutus['tuntikohtainen'] . ";" . $ret_kulutus['lampo'] . ";" . $ret_kulutus['kosteus'] . ";" . $ret_kulutus['ulkolampo'] . ";" . $ret_kulutus['ulkokosteus'] . ";<br>" ;
        }
        $db_kulutus->close();


echo "</pre>";
?>
