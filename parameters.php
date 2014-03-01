<!DOCTYPE html>
<?php
// printing out php errors for debugging
error_reporting (E_ALL | E_STRICT);
ini_set ('display_errors' , 1);
// includes
include 'modules/m_parameters.php';
?>

<html>
<head>
<link rel="stylesheet" media="only screen and (max-device-width:480px)" href="css/style_handheld.css">
<link rel="stylesheet" media="all" href="css/style_screen.css">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Parameters</title>
</head>

<body>

<h2>Parameters</h2>

<form action="<?php echo $_SERVER['PHP_SELF']; ?>" method="post">
	<p><input type="text" class="Inputfield2" name="name" value="<?php echo isset($_POST['name']) ? htmlspecialchars($_POST['name']) : ''; ?>" /> name (set, get, create, delete)</p>
	<p><input type="text" class="Inputfield2" name="value" value="<?php echo isset($_POST['value']) ? htmlspecialchars($_POST['value']) : ''; ?>" /> value (set, create)</p>
    <p>
        <select name="type" class="DropDown" size="1" >
            <option selected="selected">integer</option>
            <option>string</option>
            <option>bool</option>
            <option>date</option>
            <option>double</option>
        </select>
        datatype (create)
    </p>
    <p>
        <input type="submit" name="button2" class="Button" value="get"/>
        <input type="submit" name="button1" class="Button" value="set"/>
        <input type="submit" name="button3" class="Button" value="create"/>
        <input type="submit" name="button4" class="Button" value="delete"/>
    </p>
</form>


<?php
if (isset($_REQUEST["button1"])){ // if button1 was clicked on: set
    set_parameter($_POST['name'],$_POST['value']);
}

if (isset($_REQUEST["button2"])){ // if button2 was clicked on: get
    $result = get_parameter($_POST['name']);
    echo "value is $result";
}

if (isset($_REQUEST["button3"])){ // if button3 was clicked on: create
    if(($_POST['name'] != '') & ($_POST['value'] != '') & ($_POST['type'] != '')){
        create_parameter($_POST['name'],$_POST['value'],$_POST['type']);
    }else{
        echo 'one or more input fields are missing';
    }
}

if (isset($_REQUEST["button4"])){ // if button4 was clicked on: delete
    delete_parameter($_POST['name']);
}
?>

</body>
</html>
