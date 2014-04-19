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
          <li class="active">
            <a href="index.php">Find Book</a>
          </li>
          <li>
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
          <p>
            <select name="books" class="DropDown" size="1">
                <?php 
                    if(isset($_POST['books'])){
                        $bookID = intval(substr($_POST['books'], 2));
                    }else{
                        $bookID = 0;
                    }
                    book_select($bookID, True); 
                    ?>
            </select>
          </p>
          <p>
            <input type="submit" name="button1" class="Button" value="find book" /> <input type="submit" name="button2" class="Button" value="laser off" />
          </p>
        </form><?php
                    if (isset($_REQUEST["button1"])){ // if button1 was clicked on: find book
                        $bookID = substr($_POST['books'], 2); // convert IDxxx -> xxx
                        $message = laser_to_book($bookID);
                    }
                    if (isset($_REQUEST["button2"])){ // if button2 was clicked on: stop laser
                        set_parameter("Action", "Stop"); // this parameter is then read by the laser_daemon process
                    }
                    ?>
        <div class="Message">
            <p><?php echo $message; ?></p>
        </div>                    
      </div>
    </div>
  </body>
</html>