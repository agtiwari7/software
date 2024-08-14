<?php
$files = scandir('.');
foreach($files as $file) {
    if ($file !== '.' && $file !== '..') {
        echo "<a href=\"$file\">$file</a><br>";
    }
}
?>
