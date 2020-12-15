<?php
class Db {

	public $db;

	public function __construct($db){
		$this->db = new SQLite3($db);
		$this->init();
	}

	private function init(){
		//$this->dropStudentTable();
		$this->createStudentTable();
	}


	public function createStudentTable(){
		return $this->db->exec('CREATE TABLE IF NOT EXISTS asiakkaat (id TEXT, nimi TEXT, numero TEXT)');
	}

	public function dropStudentTable(){
		return $this->db->exec('DROP TABLE asiakkaat');
	}

	public function insert($id, $nimi, $numero){
		return $this->db->exec("INSERT INTO asiakkaat (id, nimi, numero) VALUES ('$id', '$nimi', '$numero')");
	}

	public function update($tunniste, $id, $nimi, $numero){
		return $this->db->query("UPDATE asiakkaat set id='$id', nimi='$nimi', numero='$numero' WHERE rowid=$tunniste");
	}

	public function delete($tunniste){
		return $this->db->query("DELETE FROM asiakkaat WHERE rowid=$tunniste");
	}

	public function getAll(){
		return $this->db->query("SELECT rowid, * FROM asiakkaat");
	}

	public function getById($tunniste){
		return $this->db->query("SELECT rowid, * FROM asiakkaat WHERE rowid=$tunniste");
	}
}

?>
