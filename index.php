<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<?php
  // printing out php errors for debugging
  error_reporting (E_ALL | E_STRICT);
  ini_set ('display_errors' , 1);

  include 'modules/m_books.php';
  include 'modules/m_menu.php';
  $message = "";
?>    
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
  <head>
    <link href="css/blitzer/jquery-ui-1.10.4.custom.css" rel="stylesheet" />  
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
        <?php create_menu(); ?>
      </div>
      <div class="layoutPageBody">
      <div class="ui-widget-content" style="padding:0.5em;">
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
            <input type="submit" name="button1" class="Button" value="find book" />
          </p>
        </form><?php
                    if (isset($_REQUEST["button1"])){ // if button1 was clicked on: find book
                        $bookID = substr($_POST['books'], 2); // convert IDxxx -> xxx
                        $message = laser_to_book($bookID);
                    }
                    ?>
        <div class="Message">
            <p><?php echo $message; ?></p>
        </div> 
        </div>
      </div>
    </div>
  </body>
</html>