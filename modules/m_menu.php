<?php
function create_menu(){
    
    $menu_items = array("Find Book" => "/index.php","Manage Books" => "/books.php");
    
    echo "<ul>\n";
    foreach ($menu_items as &$item) {
        if ($_SERVER['PHP_SELF'] == $item){
            echo "<li class='active'>\n";
        }else{
            echo "<li>\n";
        }
        echo "<a href='$item'>" . array_keys($menu_items,$item)[0] . "</a>\n";
        echo "</li>\n";
    }
    echo "</ul>\n";
}
?> 