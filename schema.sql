CREATE TABLE IF NOT EXISTS "hau_values" (
	"hau_v_id" INTEGER PRIMARY KEY AUTOINCREMENT,
	"pr_id" INTEGER NOT NULL,
	"gas" NUMERIC,
	"water" NUMERIC,
	"electricity" NUMERIC,
	"heating" NUMERIC,
	"garbage" NUMERIC,
	"date" TEXT,
	FOREIGN KEY("pr_id") REFERENCES "properties"("id") DEFERRABLE INITIALLY DEFERRED
);

CREATE TABLE IF NOT EXISTS "type" (
	"type_id" INTEGER PRIMARY KEY AUTOINCREMENT,
	"name"	TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS "properties" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "name" TEXT,
    "type_id" INTEGER NOT NULL,
    "hau_v_id" INTEGER NOT NULL,
    FOREIGN KEY("type_id") REFERENCES "type"("type_id"),
    FOREIGN KEY("hau_v_id") REFERENCES "hau_values"("hau_v_id") DEFERRABLE INITIALLY DEFERRED
);
