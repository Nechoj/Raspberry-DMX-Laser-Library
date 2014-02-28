<!DOCTYPE html>
<?php
// printing out php errors for debugging
error_reporting (E_ALL | E_STRICT);
ini_set ('display_errors' , 1);

include 'modules/m_books.php';
?>

<html>
<head>
<link rel="stylesheet" media="all" href="css/style_screen.css">
<link rel="stylesheet" media="only screen and (max-device-width:480px)" href="css/style_handheld.css">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Library</title>
</head>

<body>

<h1>Library</h1>

<form action="<?php echo $_SERVER['PHP_SELF']; ?>" method="post">
    <p>
        <select name="books" class="DropDown2" size="1">
            <?php book_select(isset($_POST['books']) ? substr($_POST['books'], 2) : 0); ?>
        </select>
    </p>
    <p>
        <input type="submit" name="button1" class="Button" value="find"/>
        <input type="submit" name="button2" class="Button" value="stop"/>
    </p>
</form>

<?php
if (isset($_REQUEST["button1"])){ // if button1 was clicked on: find book
    $bookID = substr($_POST['books'], 2); // convert IDxxx -> xxx
    $ret = calculate_xy($bookID);
    $command = "sudo python scripts/laser_xy.py -x " . $ret['x'] . " -y " . $ret['y'];
    //echo $command;
    exec($command);
}
if (isset($_REQUEST["button2"])){ // if button2 was clicked on: stop laser
    $command = "sudo python scripts/laser_stop.py";
    exec($command);
}
?>

</body>
</html>

