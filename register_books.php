<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<?php
  // printing out php errors for debugging
  error_reporting (E_ALL | E_STRICT);
  ini_set ('display_errors' , 1);

  include 'modules/m_books.php';
  $message = "";
?>

<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
  <head>
    <link rel="stylesheet" media="all" href="css/style_screen.css" />
    <link rel="stylesheet" media="only screen and (max-device-width:480px)" href="css/style_handheld.css" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>
      Library Management System
    </title>
  </head>
  <body>
    <div class="layoutPage">
      <div class="layoutPageHead">
        <div class="globalLogo left">
          Library Management System
        </div>
      </div>
      <div class="globalNavigationMain">
        <ul>
          <li>
            <a href="index.php">Find Book</a>
          </li>
          <li class="active">
            <a href="register_books.php">Detect Book</a>
          </li>
          <li>
            <a href="add_book.php">Add Book</a>
          </li>
          <li>
            <a href="books.php">Manage Books</a>
          </li>
        </ul>
      </div>
      <div class="layoutPageBody">
        <form action="<?php echo $_SERVER['PHP_SELF']; ?>" method="post">
            <p>Make clear view of camera to shelf and press button Step 1</p>
            <p><a onclick="document.body.className = 'wait'"><input type="submit" name="button_step1" class="Button" value="Step 1"/></a></p>
          <?php 
                if (isset($_POST['button_step1'])){
                    echo "<p>Rotate book by 90 degrees and then press button Step 2</p>\n";                
                    echo "<p><a onclick='document.body.className = \"wait\"'><input type='submit' name='button_step2' class='Button' value='Step 2'/></a></p>\n";
                    }
                ?>
        </form><?php
        if (isset($_REQUEST["button_step1"])){ // if button_step1 was clicked on
            set_parameter("Action", "Detect1"); // this parameter is then read by the laser_daemon process
            while(get_parameter("Action") != "done"){
                sleep(0.2);
            }
        }
        if (isset($_REQUEST["button_step2"])){
            set_parameter("Action", "Detect2"); // this parameter is then read by the laser_daemon process
            while(get_parameter("Action") != "done"){
                sleep(0.2);
            }            
            $row = get_parameter("row");
            if ($row==0){
                echo "\n<p>Book position not detected - try again, or, continue and enter book position data manually</p>\n";
                echo "<form action='add_book.php' method='get'>\n";
                echo "<p><input type='submit' name='button_continue' class='Button' value='Continue'/></p>\n";
                echo "</form>\n";
            }else{
                header('Location: /add_book.php');
                exit;
            }
        }
        ?>
        <div class="Message">
          <p>
            <?php echo $message; ?>
          </p>
        </div>
      </div>
    </div>
  </body>
</html>