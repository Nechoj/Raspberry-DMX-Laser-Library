<?PHP
/* This general module maintains persistent global parameters in a database.
The mysql database has got a table named parameters and with this layout:

mysql> describe parameters;
+----------+----------+------+-----+---------+-------+
| Field    | Type     | Null | Key | Default | Extra |
+----------+----------+------+-----+---------+-------+
| name     | char(20) | YES  |     | NULL    |       |
| value    | char(20) | YES  |     | NULL    |       |
| datatype | char(20) | YES  |     | NULL    |       |
+----------+----------+------+-----+---------+-------+

This table is also used by the python scripts and serves as communication channel between python and php modules
*/


function get_parameter($name){
// function get_parameters: returns the value of a parameter

    // Connecting, selecting database
    $link = mysql_connect('localhost', 'web_user', 'dbwebuserpwd')
        or die('Could not connect: ' . mysql_error());
    mysql_select_db('laser') or die('Could not select database laser');
    
    // Performing SQL query
    $query = "SELECT * FROM parameters WHERE name = '$name'";
    $result = mysql_query($query) or die('Query failed: ' . mysql_error());
    
    if (!$result) {
        echo 'Error in query: ' . mysql_error();
        exit(1);
    }
    
    $row = mysql_fetch_row($result); // first occurance of parameter only (1st row in $result)
    if(!$row){ // parameter not found
        return 'not found';
    }
    
    if ($row[2] == 'integer'){
        $ret = intval($row[1]);
    }elseif ($row[2] == 'double'){
        $ret = floatval($row[1]);
    }elseif ($row[2] == 'date'){
        try {
            $ret = new DateTime($row[1]);
        } catch (Exception $e) {
            echo $e->getMessage();
            exit(1);
        }
    }elseif ($row[2] == 'bool'){
        if ($row[1] == '1' or $row[1] == 'true' or $row[1] == 'TRUE' or $row[1] == 'True' or $row[1] == 'wahr' or $row[1] == 'WAHR'){
            $ret = true;
        }else{
            $ret = false;
        }
    }else{
        $ret = $row[1];
    }
    
    // Free result set
    mysql_free_result($result);
    // Closing connection
    mysql_close($link);
    
    return $ret;
}

function set_parameter($name,$value){
    // Connecting, selecting database
    $link = mysql_connect('localhost', 'web_user', 'dbwebuserpwd')
        or die('Could not connect: ' . mysql_error());
    mysql_select_db('laser') or die('Could not select database laser');
    
    // checking whether parameter is in database
    $query = "SELECT * FROM parameters WHERE name = '$name'";
    $result = mysql_query($query) or die('Query failed: ' . mysql_error());
    $row = mysql_fetch_row($result); // first occurance of parameter only (1st row in $result)
    if(!$row){ // parameter not found
        echo 'parameter not in database';
        exit(1);
    }
    
    // update value
    $query = "UPDATE parameters SET parameters.value = '$value' WHERE name = '$name'";
    mysql_query($query) or die('Query failed: ' . mysql_error());
    
    // Closing connection
    mysql_close($link);
}


function create_parameter($name,$value,$datatype){
    
    $allowed_types = array('integer' => 1,'string' => 1,'date' => 1, 'double' => 1, 'bool' => 1);
    
    if (array_key_exists($datatype, $allowed_types)) {
        // Connecting, selecting database
        $link = mysql_connect('localhost', 'web_user', 'dbwebuserpwd')
            or die('Could not connect: ' . mysql_error());
        mysql_select_db('laser') or die('Could not select database laser');
    
        // checking whether parameter already is in database
        $query = "SELECT * FROM parameters WHERE name = '$name'";
        $result = mysql_query($query) or die('Query failed: ' . mysql_error());
        $row = mysql_fetch_row($result); // first occurance of parameter only (1st row in $result)
        if($row){ // parameter found
            echo 'parameter is already in database';
            exit(1);
        }
    
        // insert new parameter
        $query = "INSERT INTO parameters VALUES ('$name','$value','$datatype')";
        mysql_query($query) or die('Query failed: ' . mysql_error());
    
        // Closing connection
        mysql_close($link);
    }else{
        echo 'datatype not allowed!'; 
        exit(1);
    }
}

function delete_parameter($name)
{
    // Connecting, selecting database
    $link = mysql_connect('localhost', 'web_user', 'dbwebuserpwd')
        or die('Could not connect: ' . mysql_error());
    mysql_select_db('laser') or die('Could not select database laser');
    
    // checking whether parameter is in database
    $query = "SELECT * FROM parameters WHERE name = '$name'";
    $result = mysql_query($query) or die('Query failed: ' . mysql_error());
    $row = mysql_fetch_row($result); // first occurance of parameter only (1st row in $result)
    if(!$row){ // parameter not found
        echo 'parameter not in database';
        exit(1);
    }
    
    // delete parameter
    $query = "DELETE FROM parameters WHERE name = '$name'";
    mysql_query($query) or die('Query failed: ' . mysql_error());
    
    // Closing connection
    mysql_close($link);
    echo "parameter $name has been deleted";
}

?>