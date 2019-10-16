<?php

// error display
ini_set("display_errors", 0);
error_reporting(E_ALL ^ E_NOTICE);
error_reporting(E_ALL ^ E_WARNING);

// header
header('Access-Control-Allow-Origin:*');

// Response class
class Response {
    public $aid;
    public $tid;
    public $pn;
}

// db conn
try {
    $conn = new PDO('mysql:host=localhost;dbname=nbph;charset=utf8', 'root', 'root', array(PDO::ATTR_PERSISTENT => true));
} catch (PDOException $e) {
    echo('<script>alert("' . $e->getMessage() . '")</script>');
    die(0);
}

// GET param
$aid = -1;
if (isset($_GET['aid'])) {
    $aid = intval($_GET['aid']);
}

// init resp
$resp = new Response();
$resp->aid = $aid;
$resp->tid = -1;
$resp->pn = -1;

// check param
if ($aid <= 0) {
    echo(json_encode($resp, JSON_UNESCAPED_UNICODE));
    die(0);
}

// 01 query video
$sql1 = 'select * from nbph.video where aid = '.$aid;
if ($result = $conn->query($sql1)) {
    if ($row = $result->fetch(PDO::FETCH_ASSOC)) {
        $tid = intval($row['tid']);
        $resp->tid = $tid;
        $create = intval($row['create']);
    } else {
        echo(json_encode($resp, JSON_UNESCAPED_UNICODE));
        die(0);
    }
} else {
    echo(json_encode($resp, JSON_UNESCAPED_UNICODE));
    die(0);
}

// 02 get count
$sql2 = 'select count(*) from nbph.video where tid = '.$tid.' && `create` >= '.$create;
if ($result = $conn->query($sql2)) {
    if ($row = $result->fetch(PDO::FETCH_ASSOC)) {
        $count = $row['count(*)'];
    } else {
        echo(json_encode($resp, JSON_UNESCAPED_UNICODE));
        die(0);
    }
} else {
    echo(json_encode($resp, JSON_UNESCAPED_UNICODE));
    die(0);
}

// 03 calc pn
$pn = ceil($count / 50);
$resp->pn = $pn;
echo(json_encode($resp, JSON_UNESCAPED_UNICODE));
