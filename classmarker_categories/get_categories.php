<?php
include 'ClassMarkerApiClient.php';
include 'config.inc';

$cm_client = new ClassMarkerClient($key, $secret);
$json_response = $cm_client->getAllCategories();
echo $json_response;
?>
