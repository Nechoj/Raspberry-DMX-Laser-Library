<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<?php
  // printing out php errors for debugging
  error_reporting (E_ALL | E_STRICT);
  ini_set ('display_errors' , 1);

  include 'modules/m_books.php';
  $message = "";
?>
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>

    <script type="text/javascript">
//<![CDATA[
    function CheckSelection () {
    var sel_i = document.create_book.books.selectedIndex;
    if(sel_i > 0)
        var fields = document.create_book.books.options[sel_i].text.split(" // ");
        document.getElementsByName("title")[0].value = fields[0];
        document.getElementsByName("author")[0].value = fields[1];
    }
    //]]>
    </script>
    <link rel="stylesheet" media="all" href="css/style_screen.css" />
    <link rel="stylesheet" media="only screen and (max-device-width:480px)" href="css/style_handheld.css" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>
      Library Management System
    </title>
  </head>
  <body onload="CheckSelection()">
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
          <li class="active">
            <a href="add_book.php">Add Book</a>
          </li>
          <li>
            <a href="books.php">Manage Books</a>
          </li>
        </ul>
      </div>
      <div class="layoutPageBody">
        <p>
          Select book from list, or, type in title and author:
        </p>
        <?php 
            if (isset($_REQUEST["button_sync"])){ // if button_sync was clicked: execute this function *before* the select list is being queried
            $message = zotero_sync();
        }
        ?>
        <form name="create_book" action="<?php $_SERVER['PHP_SELF'] ?>" method="post" id="create_book">
          <p>
            <select name="books" class="DropDown" size="1" onchange="CheckSelection()">
              <?php book_select(isset($_POST['books']) ? substr($_POST['books'], 2) : 0); ?>
            </select> <input type="submit" name="button_sync" class="Button" value="zotero sync" />
          </p>
          <p>
            <input type="text" class="Inputfield2" name="title" value="" /> title <!-- value is set in function CheckSelection() -->
          </p>
          <p>
            <input type="text" class="Inputfield2" name="author" value="" /> author <!-- value is set in function CheckSelection() -->
          </p>
          <p>
            <input type="text" class="Inputfield1" name="row" value="<?php echo isset($_POST['row']) ? htmlentities($_POST['row']) : get_parameter('row'); ?>" /> row (top row is 1)
          </p>
          <p>
            <input type="text" class="Inputfield1" name="position" value="<?php echo isset($_POST['position']) ? htmlentities($_POST['position']) : get_parameter('dist_x'); ?>" /> position (cm from left border)
          </p>
          <p>
            Check whether laser is pointing to the requested book.<br />
            If not, try automatic detection again, or, change row and distance manually
          </p>
          <p>
            <input type="submit" name="button_test" class="Button" value="test position" /> <input type="submit" name="button_off" class="Button" value="laser off" />
          </p>
          <p>
            If everything OK:
          </p>
          <p>
            <input type="submit" name="button_store" class="Button" value="add book" />
          </p>
        </form><?php
        if (isset($_REQUEST["button_test"])){ // if button_test was clicked
            laser_to_position($_POST['row'], $_POST['position']);    
        }
        if (isset($_REQUEST["button_off"])){ // if button_test was clicked
            set_parameter("Action", "Stop"); // this parameter is then read by the laser_daemon process    
        }
        if (isset($_REQUEST["button_store"])){ // if button_store was clicked
            $bookID = substr($_POST['books'], 2);
            if(intval($bookID)>0){ // book has been selected
                set_location($bookID, $_POST['row'], $_POST['position']);
                $message = "location  for book with ID $bookID set";
            }elseif(($_POST['title']!='') & ($_POST['author']!='') & ($_POST['row']!='') & ($_POST['position']!='')){
                $bookID = create_book(html_entity_decode($_POST['title']),html_entity_decode($_POST['author']),$_POST['row'],$_POST['position']);
                if(is_numeric($bookID)){
                    $message = "book created with ID $bookID";
                }else{
                    $message = "creation failed";
                }        
            }else{
                $message = "input parameter missing";
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