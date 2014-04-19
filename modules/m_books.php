<?PHP
/* ths modules manages the books table and
calculates the x and y coordinates of the laser
from the position of the book in the shelf
  
the layout of the table books in DB laser is:

mysql> describe books;
+----------+-----------+------+-----+---------+----------------+
| Field    | Type      | Null | Key | Default | Extra          |
+----------+-----------+------+-----+---------+----------------+
| bookID   | int(11)   | NO   | PRI | NULL    | auto_increment |
| title    | char(255) | YES  |     | NULL    |                |
| author   | char(255) | YES  |     | NULL    |                |
| row      | int(11)   | YES  |     | NULL    |                |
| position | int(11)   | YES  |     | NULL    |                |
+----------+-----------+------+-----+---------+----------------+

row: top row in library is number 1, number of row increases from top to bottom
position: distance of book from left border of library, in cm
*/

include 'm_parameters.php';
  
function create_book($title, $author, $row, $position){
// inserts a book into the database books
// if book already exists, only row and position is updated
// returns the bookID

    // Connecting, selecting database
    $link = mysql_connect('localhost', 'web_user', 'dbwebuserpwd')
        or die('Could not connect: ' . mysql_error());
    mysql_select_db('laser') or die('Could not select database laser');
    
    // check whether book is already in the db
    $query = "SELECT * FROM books WHERE (title = '$title') AND (author = '$author')";
    $result = mysql_query($query) or die('Query failed: ' . mysql_error());
    if (!$result) {
        echo 'Error in query 37: ' . mysql_error();
        exit(1);
    }    
    
    $dbrow = mysql_fetch_row($result);
    if($dbrow){ // book found, just update row and position
        $bookID = $dbrow[0];
        mysql_query("UPDATE books SET row = $row, position = $position WHERE bookID = $bookID") OR die('UPDATE failed 50: ' . mysql_error());
    }else{ // insert new book
        $query = "INSERT INTO books (title,author,row,position) VALUES ('$title','$author','$row','$position')";
        mysql_query($query) or die('INSERT failed 53: ' . mysql_error());

        // get bookID of new book entry
        $query = "SELECT * FROM books WHERE (title = '$title') AND (author = '$author')";
        $result = mysql_query($query) or die('Query failed: ' . mysql_error());
        if (!$result) {
            echo 'Error in query 1: ' . mysql_error();
            exit(1);
        }
        $dbrow = mysql_fetch_row($result); // first occurance of book only (1st row in $result)
    }    
    // Closing connection
    mysql_close($link);
    return $dbrow[0]; // bookID	
}


function delete_book($bookID){
// function to delete a single book entry in table books

    // Connecting, selecting database
    $link = mysql_connect('localhost', 'web_user', 'dbwebuserpwd')
        or die('Could not connect: ' . mysql_error());
    mysql_select_db('laser') or die('Could not select database laser');
    
    // checking whether title is in database
    $query = "SELECT * FROM books WHERE bookID = '$bookID'";
    $result = mysql_query($query) or die('Query failed 4: ' . mysql_error());
    $dbrow = mysql_fetch_row($result); // first occurance of parameter only (1st row in $result)
    if(!$dbrow){ // parameter not found
        echo "book not in database";
        exit(1);
    }
    // delete parameter
    $query = "DELETE FROM books WHERE bookID = '$bookID'";
    mysql_query($query) or die('Query failed 3: ' . mysql_error());
    
    // Closing connection
    mysql_close($link);
}

function book_select($bookID = 0, $with_position = False){
// function to create <options> for a html <select> drop-down list with all books in the database
// parameter bookID tells, which one is selected (optional)

    // Connecting, selecting database
    $link = mysql_connect('localhost', 'web_user', 'dbwebuserpwd')
        or die('Could not connect: ' . mysql_error());
    mysql_select_db('laser') or die('Could not select database laser');
    
    $query = "";
    if ($with_position){
        $query = "SELECT * FROM books WHERE row != 0 ORDER BY title";
    }else{
        $query = "SELECT * FROM books ORDER BY title";
    }
    $result = mysql_query($query) OR die(mysql_error());
    
    echo "<option></option>\n";
    while($dbrow = mysql_fetch_row($result)){
        if($bookID == $dbrow[0]){
            echo "<option selected value='ID" . $dbrow[0] . "'>" . htmlentities($dbrow[1],$double_encode = false) . " // " . htmlentities($dbrow[2], $double_encode = false) . "</option>\n";
        }else{
            echo "<option value='ID" . $dbrow[0] . "'>" . htmlentities($dbrow[1],$double_encode = false) . " // " . htmlentities($dbrow[2],$double_encode = false) . "</option>\n";
        }
    }
    // Free result set
    mysql_free_result($result);
    // Closing connection
    mysql_close($link);
}


function get_location($bookID){
// function get attributes row and position for a book

    // initialising variables
    $row=1;
    $cm=0;
    // Connecting, selecting database
    $link = mysql_connect('localhost', 'web_user', 'dbwebuserpwd')
        or die('Could not connect: ' . mysql_error());
    mysql_select_db('laser') or die('Could not select database laser');
    
    // get parameters of that book
    $query = "SELECT * FROM books WHERE bookID = '$bookID'";
    $result = mysql_query($query) or die('Query failed 141: ' . mysql_error());
    $dbrow = mysql_fetch_row($result); // first occurance of parameter only (1st row in $result)
    if($dbrow){// we found the book
        return array('row' => $dbrow[3], 'dist' => $dbrow[4]);
    }else{
        return array('row' => 0, 'dist' => 0);
    }

    // Closing connection
    mysql_close($link);
}


function set_location($bookID, $row, $position){
// function to update row and position for a book

    // Connecting, selecting database
    $link = mysql_connect('localhost', 'web_user', 'dbwebuserpwd')
        or die('Could not connect: ' . mysql_error());
    mysql_select_db('laser') or die('Could not select database laser');
    
    mysql_query("UPDATE books SET row = $row, position = $position WHERE bookID = $bookID") OR die(mysql_error());
    
    // Closing connection
    mysql_close($link);
}


function laser_to_book($bookID){
// directs the laser to a book
// communication with laser_daemon is via special database parameters

    // initialising variables
    $row=1;
    $cm=0;
    // Connecting, selecting database
    $link = mysql_connect('localhost', 'web_user', 'dbwebuserpwd')
        or die('Could not connect: ' . mysql_error());
    mysql_select_db('laser') or die('Could not select database laser');
    
    // get parameters of that book
    $query = "SELECT * FROM books WHERE bookID = '$bookID'";
    $result = mysql_query($query) or die('Query failed 5: ' . mysql_error());
    $dbrow = mysql_fetch_row($result); // first occurance of parameter only (1st row in $result)
    if($dbrow){// we found the book
        $row = $dbrow[3]; // parameter row
        $cm = $dbrow[4]; // parameter position
    }else{
        return 'book not found';
    }
    
    // the commands to the laser are stored in table parameters and read by the laser_daemon.py, which then directs the laser
    // process laser_daemon.py must be running!
    $value = (string)(1000*$row+$cm);
    $query = "UPDATE parameters SET parameters.value = '$value' WHERE name = 'L_rcm'"; // this parameter is read by the laser_daemon.py
    mysql_query($query) or die('Query failed: ' . mysql_error());
    $query = "UPDATE parameters SET parameters.value = 'Move_rcm' WHERE name = 'Action'"; // this parameter is read by the laser_daemon.py
    mysql_query($query) or die('Query failed: ' . mysql_error());    
    
    // Free result set
    mysql_free_result($result);
    // Closing connection to DB (note: DB should be closed before using set_parameter() which opens DB again)
    mysql_close($link);
}

function laser_to_position($row, $dist){
// directs the laser to position defined by parameters $row and $dist
// communication with laser_daemon is via special database parameters

    // Connecting, selecting database
    $link = mysql_connect('localhost', 'web_user', 'dbwebuserpwd')
        or die('Could not connect: ' . mysql_error());
    mysql_select_db('laser') or die('Could not select database laser');

    // the commands to the laser are stored in table parameters and read by the laser_daemon.py, which then directs the laser
    // process laser_daemon.py must be running!
    $value = (string)(1000*$row+$dist);
    $query = "UPDATE parameters SET parameters.value = '$value' WHERE name = 'L_rcm'"; // this parameter is read by the laser_daemon.py
    mysql_query($query) or die('Query failed: ' . mysql_error());
    $query = "UPDATE parameters SET parameters.value = 'Move_rcm' WHERE name = 'Action'"; // this parameter is read by the laser_daemon.py
    mysql_query($query) or die('Query failed: ' . mysql_error());    
    
    // Closing connection to DB (note: DB should be closed before using set_parameter() which opens DB again)
    mysql_close($link);
}


function zotero_sync(){
// function to fetch and read out the zotero db file zotero.sqlite and stores the entries in the books db
    
    // get new sqlite-file from zotero cloud server
    $ftp_server = "192.168.178.2";
    $ftp_user = "pi";
    $ftp_pass = "piuserpwd";
    $local_file = "/home/pi/www/data/zotero.sqlite";
    $server_file = "/Zotero/zotero.sqlite";
    
    $conn_id = ftp_connect($ftp_server) or die("Couldn't connect to $ftp_server");
    
    if (@ftp_login($conn_id, $ftp_user, $ftp_pass)){
        if (!ftp_get($conn_id, $local_file, $server_file, FTP_BINARY)) {
            return "error in ftp_get()";
        }
    }else{
        return "ftp login failed";
    }    
    ftp_close($conn_id);

    // read out book table from zotero sqlite db
    $query = "SELECT
    title.value AS TITLE,
    subtitle.value AS SUBTITLE,
    t.typeName AS TYPE,
    isbn.value AS ISBN,
    c1.firstName AS AUTHOR_1_FIRST,
    c1.lastName AS AUTHOR_1_LAST,
    i.dateAdded AS DATE_ADDED,
    i.key AS ZOTERO_KEY

    FROM
    items i

    INNER JOIN
    itemDataValues title
    ON
    title.valueID = (SELECT itemData.valueID FROM itemData WHERE itemData.fieldID = (SELECT fieldID FROM fields WHERE fields.fieldName = 'title' LIMIT 1) AND itemData.itemID=i.itemID LIMIT 1)

    LEFT JOIN
    itemDataValues subtitle
    ON
    subtitle.valueID = (SELECT itemData.valueID FROM itemData WHERE itemData.fieldID = (SELECT fieldID FROM fields WHERE fields.fieldName = 'shortTitle' LIMIT 1) AND itemData.itemID=i.itemID LIMIT 1)
    
    LEFT JOIN
    itemTypes t
    ON
    t.itemTypeID = i.itemTypeID

    LEFT JOIN
    collectionItems coll
    ON
    coll.itemID = i.itemID

    LEFT JOIN
    itemDataValues isbn
    ON
    isbn.valueID = (SELECT itemData.valueID FROM itemData WHERE itemData.fieldID = (SELECT fieldID FROM fields WHERE fields.fieldName = 'ISBN' LIMIT 1) AND itemData.itemID=i.itemID LIMIT 1)

    LEFT JOIN
    creatorData c1
    ON
    c1.creatorDataID = (SELECT creatorDataID FROM creators WHERE creatorID = (SELECT creatorID FROM itemCreators WHERE itemID = i.itemID ORDER BY orderIndex LIMIT 0,1) LIMIT 1)

    LEFT JOIN
    creatorTypes ct1
    ON
    ct1.creatorTypeID = (SELECT creatorTypeID FROM itemCreators WHERE itemID = i.itemID ORDER BY orderIndex LIMIT 0,1)

    LEFT JOIN
    deletedItems
    ON i.itemID = deletedItems.itemID

    WHERE deletedItems.itemID IS NULL
    AND  t.typeName = 'book'
    ";
    //     AND coll.collectionID = (SELECT collectionID FROM collections WHERE collectionName = 'Bibliothek FBA' LIMIT 0,1)
    
    $db = new SQLite3('data/zotero.sqlite');
    $results = $db->query($query);

    // Connecting, selecting mySQL database
    $link = mysql_connect('localhost', 'web_user', 'dbwebuserpwd')
        or die('Could not connect: ' . mysql_error());
    mysql_select_db('laser') or die('Could not select database laser');
       
    // transfer book items   
    while ($row = $results->fetchArray()) {
        if($row[1] != Null){ // short title
            $title = $row[1];
        }else{
            $title = $row[0]; // long title
        }
        $author = $row[4] . " " . $row[5];
        // check whether book is already in the db
        $query = "SELECT * FROM books WHERE (title = '$title') AND (author = '$author')";
        $res = mysql_query($query) or die('Query failed: ' . mysql_error());
        if (!$res) {
            return 'Error in query 264: ' . mysql_error();
        }    
    
        $row = mysql_fetch_row($res);
        if(!$row){ // book not yet there -> insert
            $query = "INSERT INTO books (title,author,row,position) VALUES ('$title','$author',0,0)";
            mysql_query($query) or die('INSERT failed 271: ' . mysql_error());
        }
    }
    
    // Closing connections to DBs
    $db->close();
    mysql_close($link);
}
?>