<!-- PARAMETERS -->
<?php
	$p = $_REQUEST['p'];
	if ($p == "") $p = "profil";
?>

<!-- HEAD -->
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="fr" lang="fr">
<head>
  <meta charset="UTF-8">
	<link rel="stylesheet" href="style.css" type="text/css"/>
	<link rel="shortcut icon" href="favicon.ico" type="image/x-icon">
	<link rel="icon" href="favicon.ico" type="image/x-icon">
	<?php
		echo "<title>François Lareau";
		switch ($p) {
				case "publis":
						echo " - Publications";
						break;
		};
		echo "</title>";
	?>
</head>

<!-- BODY -->
<body>
	<div class="container">

		<!-- HEADER -->
		<header>
			<div id="name">
				<h1>François Lareau</h1>
				<h2>
					Professeur agrégé<br/>
					<a href="http://olst.ling.umontreal.ca">OLST</a>,
					<a href="http://www.ling.umontreal.ca">Université de Montréal</a>
				</h2>
			</div>
			<nav>
				<ul>
					<li><a href="index.php?p=profil">Profil</a></li>
					<li><a href="index.php?p=publis">Publications</a></li>
				</ul>
			</nav>
		</header>

		<!-- CONTENT -->
		<div id="content">
			<?php
				switch ($p) {
					case "publis":
						$bodyfile = "publis.php";
						$datecheck = "publis.bib";
						break;
					default:
						$p = "profil";
						$bodyfile = "profil.php";
						$datecheck = $bodyfile;
				}
				include($bodyfile);
			?>
			<br/>
			<br/>
		</div>

		<!-- FOOTER -->
		<div id="footer">
			<?php echo "<p>Dernière mise à jour: " . date ("Y-m-d", filemtime($datecheck)) . "</p>"; ?>
		</div>

	</div>
</body>
</html>
