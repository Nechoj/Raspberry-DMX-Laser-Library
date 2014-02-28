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
// inserts a book into the database books and returns the bookID

// Connecting, selecting database
$link = mysql_connect('localhost', 'web_user', 'dbwebuserpwd')
   	or die('Could not connect: ' . mysql_error());
mysql_select_db('laser') or die('Could not select database laser');

// insert new book
$query = "INSERT INTO books (title,author,row,position) VALUES ('$title','$author','$row','$position')";
mysql_query($query) or die('Query failed: ' . mysql_error());

// get bookID
$query = "SELECT * FROM books WHERE (title = '$title') AND (author = '$author')";
$result = mysql_query($query) or die('Query failed: ' . mysql_error());
if (!$result) {
    echo 'Error in query: ' . mysql_error();
    exit(1);
}
$dbrow = mysql_fetch_row($result); // first occurance of book only (1st row in $result)

// Closing connection
mysql_close($link);
return $dbrow[0]; // bookID	
}

// function to delete a single book entry in table books
function delete_book($bookID)
{
// Connecting, selecting database
$link = mysql_connect('localhost', 'web_user', 'dbwebuserpwd')
    or die('Could not connect: ' . mysql_error());
mysql_select_db('laser') or die('Could not select database laser');

// checking whether title is in database
$query = "SELECT * FROM books WHERE bookID = '$bookID'";
$result = mysql_query($query) or die('Query failed: ' . mysql_error());
$dbrow = mysql_fetch_row($result); // first occurance of parameter only (1st row in $result)
if(!$dbrow){ // parameter not found
    echo "book not in database";
    exit(1);
}
// delete parameter
$query = "DELETE FROM books WHERE bookID = '$bookID'";
mysql_query($query) or die('Query failed: ' . mysql_error());

// Closing connection
mysql_close($link);
}

// function to create <options> for a html <select> drop-down list with all books in the database
// parameter bookID tells, which one is selected (optional)
function book_select($bookID = 0){
// Connecting, selecting database
$link = mysql_connect('localhost', 'web_user', 'dbwebuserpwd')
    or die('Could not connect: ' . mysql_error());
mysql_select_db('laser') or die('Could not select database laser');

$result = mysql_query("SELECT * FROM books ORDER BY title") OR die(mysql_error());

while($dbrow = mysql_fetch_row($result)){
    if($bookID == $dbrow[0]){
        echo '<option selected value="ID' . $dbrow[0] . '">' . $dbrow[1] . '</option>';
    }else{
        echo '<option value="ID' . $dbrow[0] . '">' . $dbrow[1] . '</option>';
    }
}
// Free result set
mysql_free_result($result);
// Closing connection
mysql_close($link);
}

// function to update row and position for a book
function set_location($bookID, $row, $position){
// Connecting, selecting database
$link = mysql_connect('localhost', 'web_user', 'dbwebuserpwd')
    or die('Could not connect: ' . mysql_error());
mysql_select_db('laser') or die('Could not select database laser');

mysql_query("UPDATE books SET row = $row, position = $position WHERE bookID = $bookID") OR die(mysql_error());

// Closing connection
mysql_close($link);
}

// function to calculate the x and y coordinates for the laser for a given book
function calculate_xy($bookID){
// initialising variables
$row=1;
$position=0;
// Connecting, selecting database
$link = mysql_connect('localhost', 'web_user', 'dbwebuserpwd')
    or die('Could not connect: ' . mysql_error());
mysql_select_db('laser') or die('Could not select database laser');

// get parameters of that book
$query = "SELECT * FROM books WHERE bookID = '$bookID'";
$result = mysql_query($query) or die('Query failed: ' . mysql_error());
$dbrow = mysql_fetch_row($result); // first occurance of parameter only (1st row in $result)
if($dbrow){// we found the book
    $row = $dbrow[3]; // parameter row
    $position = $dbrow[4]; // parameter position
}else{
    echo 'book not found <br />';
    exit(1);
}
// Free result set
mysql_free_result($result);
// Closing connection to DB (note: DB should be closed before using get_parameter() which opens DB again)
mysql_close($link);

// get y-coord of row from table parameters
$y = get_parameter("y_row_$row");

// get relevant x-parameters
$x_left_dist = get_parameter('x_left_dist'); // distance of leftmost laser position from left border of book shelf (in cm)
$x_right_dist = get_parameter('x_right_dist'); // distance of rightmost laser position from left border of book shelf (in cm)
$x_left = get_parameter('x_left'); // value for channel 'move to x' for leftmost laser position
$x_right = get_parameter('x_right'); // value for channel 'move to x' for rightmost laser position

// calculate the width of a step
$stepwidth = ($x_right_dist- $x_left_dist)/abs($x_right-$x_left);
//echo "$stepwidth <br />";
// calculate the x-coordinate
if($position < $x_left_dist){ // book is outside left range
    $x = $x_left;
}elseif($position > $x_right_dist){ // book is outside right range
    $x = $x_right;
}elseif($x_right>$x_left){ // x-values increase from left to right
    $x = $x_left + ($position - $x_left_dist)/$stepwidth;
}else{ // x-values decrease from left to right
    $x = $x_left - ($position - $x_left_dist)/$stepwidth;
}

$x = (integer)$x;
//echo "x: $x, y: $y <br />";
return array("x" => $x, "y" => $y);
}

?>