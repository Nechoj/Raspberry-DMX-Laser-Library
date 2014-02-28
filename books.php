<!DOCTYPE html>
<?php
// printing out php errors for debugging
error_reporting (E_ALL | E_STRICT);
ini_set ('display_errors' , 1);
// includes
include 'modules/m_books.php';
$message = '';
?>

<html>
<head>
<link rel="stylesheet" media="only screen and (max-device-width:480px)" href="css/style_handheld.css">
<link rel="stylesheet" media="all" href="css/style_screen.css">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Books</title>
</head>

<body>

<h2>Books</h2>
<hr />
<h3>Create books in the DB</h3>

<form action="<?php echo $_SERVER['PHP_SELF']; ?>" method="post">
	<p><input type="text" class="Inputfield2" name="title" value="<?php echo isset($_POST['title']) ? htmlspecialchars($_POST['title']) : ''; ?>" /> title</p>
	<p><input type="text" class="Inputfield2" name="author" value="<?php echo isset($_POST['author']) ? htmlspecialchars($_POST['author']) : ''; ?>" /> author</p>
    <p><input type="text" class="Inputfield1" name="row" value="<?php echo isset($_POST['row']) ? htmlspecialchars($_POST['row']) : ''; ?>" /> row (top row is 1)</p>
    <p><input type="text" class="Inputfield1" name="position" value="<?php echo isset($_POST['position']) ? htmlspecialchars($_POST['position']) : ''; ?>" /> 
        position (cm from left border)</p>
    <p>
        <input type="submit" name="button1" class="Button" value="create book"/>
    </p>
</form>


<?php
if (isset($_REQUEST["button1"])){ // if button1 was clicked on: create
    if(($_POST['title']!='') & ($_POST['author']!='') & ($_POST['row']!='') & ($_POST['position']!='')){
        $bookID = create_book($_POST['title'],$_POST['author'],$_POST['row'],$_POST['position']);
        if(is_numeric($bookID)){
            $message = "book created with ID $bookID";
        }else{
            echo "creation failed";
        }        
    }else{
        echo "input parameter missing";
    }
}
?>

<hr />
<h3>Delete books from DB</h3>

<form action="<?php echo $_SERVER['PHP_SELF']; ?>" method="post">
    <p>
        <select name="books1" class="DropDown2" size="1">
            <?php book_select(isset($_POST['books1']) ? substr($_POST['books1'], 2) : 0); ?>
        </select> select title
    </p>
    <p><input type="submit" name="button2" class="Button" value="delete"/></p>
</form>

<?php
if (isset($_REQUEST["button2"])){ // if button2 was clicked on: create
    $bookID = substr($_POST['books1'], 2);
    delete_book($bookID);
    $message = "book deleted";
}
?>

<hr />
<h3>Set location parameter of books</h3>

<form action="<?php echo $_SERVER['PHP_SELF']; ?>" method="post">
    <p>
        <select name="books2" class="DropDown2" size="1">
            <?php book_select(isset($_POST['books2']) ? substr($_POST['books2'], 2) : 0); ?>
        </select> select title
    </p>
    <p><input type="text" class="Inputfield1" name="row2" value="<?php echo isset($_POST['row2']) ? htmlspecialchars($_POST['row2']) : ''; ?>" /> row (top row is 1)</p>
    <p><input type="text" class="Inputfield1" name="position2" value="<?php echo isset($_POST['position2']) ? htmlspecialchars($_POST['position2']) : ''; ?>" /> 
        position (cm from left border)</p>
    <p><input type="submit" name="button3" class="Button" value="set location"/></p>
</form>

<?php
if (isset($_REQUEST["button3"])){ // if button3 was clicked on: create
    if(($_POST['row2']!='') & ($_POST['position2']!='')){
        $bookID = substr($_POST['books2'], 2);
        set_location($bookID, $_POST['row2'], $_POST['position2']);
        $message = "location parameter set";
    }else{
        echo "input parameter missing";
    }
}

?>
<hr />
<div class="Message">
<p><?php echo $message; ?></p>
</div>

</body>
</html>
