<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<?php
  // printing out php errors for debugging
  error_reporting (E_ALL | E_STRICT);
  ini_set ('display_errors' , 1);

  include 'modules/m_books.php';
  $message = '';
  $row = '';
  $dist = '';
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
          <li>
            <a href="register_books.php">Detect Book</a>
          </li>
          <li>
            <a href="add_book.php">Add Book</a>
          </li>
          <li class="active">
            <a href="books.php">Manage Books</a>
          </li>
        </ul>
      </div>
      <div class="layoutPageBody">
        <h3>
          Get and Set Location of Books
        </h3>
        <?php
                if (isset($_POST['row2'])) {
                    $row = $_POST['row2'];
                    $dist = $_POST['dist2'];
                    if (isset($_REQUEST["button3"])){ // if button3 was clicked on
                        $bookID = substr($_POST['books2'], 2);
                        $pos = get_location($bookID);
                        $row = $pos['row'];
                        $dist = $pos['dist'];
                    }    
                    if (isset($_REQUEST["button4"])){ // if button4 was clicked on
                        if(($_POST['row2']!='') & ($_POST['dist2']!='')){
                            $bookID = substr($_POST['books2'], 2);
                            set_location($bookID, $_POST['row2'], $_POST['dist2']);
                            $message = "location parameter set";
                        }else{
                            $message =  "input parameter missing";
                        }
                    }
                }
            ?>
        <form action="<?php echo $_SERVER['PHP_SELF']; ?>" method="post">
          <p>
            <select name="books2" class="DropDown" size="1">
              <?php book_select(isset($_POST['books2']) ? substr($_POST['books2'], 2) : 0); ?>
            </select> select title
          </p>
          <p>
            <input type="text" class="Inputfield1" name="row2" value="<?php echo isset($_POST['row2']) ? htmlspecialchars($row) : ''; ?>" /> row (top row is 1)
          </p>
          <p>
            <input type="text" class="Inputfield1" name="dist2" value="<?php echo isset($_POST['dist2']) ? htmlspecialchars($dist) : ''; ?>" /> position (cm from left border)
          </p>
          <p>
            <input type="submit" name="button3" class="Button" value="get location" /><input type="submit" name="button4" class="Button" value="set location" />
          </p>
        </form>
        <hr />
        <h3>
          Delete books from DB
        </h3>
        <form action="<?php echo $_SERVER['PHP_SELF']; ?>" method="post">
          <p>
            <select name="books1" class="DropDown" size="1">
              <?php book_select(isset($_POST['books1']) ? substr($_POST['books1'], 2) : 0); ?>
            </select> select title
          </p>
          <p>
            <input type="submit" name="button2" class="Button" value="delete" />
          </p>
        </form><?php
            if (isset($_REQUEST["button2"])){ // if button2 was clicked on: create
                $bookID = substr($_POST['books1'], 2);
                delete_book($bookID);
                $message = "book deleted";
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