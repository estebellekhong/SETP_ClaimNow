<?php
	$Claim_Category = $_POST['Claim_Category'];
	$Claim_Amount_SGD = $_POST['Claim_Amount_SGD'];
	$Claim_Date= $_POST['Claim_Date'];
	$Claim_Desc = $_POST['Claim_Desc'];
	
	// Database connection
	$conn = new mysqli("34.87.75.110:3306","claimnow_admin","P@$$word","ClaimNow");
	if($conn->connect_error){
		echo "$conn->connect_error";
		die("Connection Failed : ". $conn->connect_error);
	} else {
		$stmt = $conn->prepare("insert into expense_claim(Claim_Category, Claim_Amount_SGD, Claim_Date, Claim_Desc) values(?, ?, ?, ?)");
		$stmt->bind_param("sdss", $Claim_Category, $Claim_Amount_SGD, $Claim_Date, $Claim_Desc);
		$execval = $stmt->execute();
		echo $execval;
		echo "Claim submitted!";
		$stmt->close();
		$conn->close();
	}
?>