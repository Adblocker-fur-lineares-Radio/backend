CREATE TABLE IF NOT EXISTS "radios" (
  "id" SERIAL PRIMARY KEY,
  "name" text,
  "status_id" integer,
  "currently_playing" text,
  "current_interpret" text,
  "stream_url" text,
  "logo_url" text
);

CREATE TABLE IF NOT EXISTS "radio_states" (
  "id" integer PRIMARY KEY,
  "label" text
);

CREATE TABLE IF NOT EXISTS "radio_genres" (
  "radio_id" integer,
  "genre_id" integer
);

CREATE TABLE IF NOT EXISTS "genres" (
  "id" integer PRIMARY KEY,
  "name" text
);

CREATE TABLE IF NOT EXISTS "connections" (
  "id" integer PRIMARY KEY,
  "search_query" text,
  "search_without_ads" bool,
  "search_remaining_update" integer,
  "preference_music" bool,
  "preference_talk" bool,
  "preference_news" bool,
  "preference_ad" bool
);

CREATE TABLE IF NOT EXISTS "connection_preferred_radios" (
  "radio_id" integer,
  "connection_id" integer
);

CREATE TABLE IF NOT EXISTS "connection_preferred_genres" (
  "connection_id" integer,
  "genre_id" integer
);

CREATE TABLE IF NOT EXISTS "connection_search_favorites" (
  "radio_id" integer,
  "connection_id" integer
);

CREATE TABLE IF NOT EXISTS "radio_ad_time" (
  "radio_id" integer,
  "ad_start_time" timestamp
);

ALTER TABLE "radios" ADD FOREIGN KEY ("status_id") REFERENCES "radio_states" ("id");

ALTER TABLE "radio_genres" ADD FOREIGN KEY ("radio_id") REFERENCES "radios" ("id");

ALTER TABLE "radio_genres" ADD FOREIGN KEY ("genre_id") REFERENCES "genres" ("id");

ALTER TABLE "connection_preferred_radios" ADD FOREIGN KEY ("radio_id") REFERENCES "radios" ("id");

ALTER TABLE "connection_preferred_radios" ADD FOREIGN KEY ("connection_id") REFERENCES "connections" ("id");

ALTER TABLE "connection_preferred_genres" ADD FOREIGN KEY ("connection_id") REFERENCES "connections" ("id");

ALTER TABLE "connection_preferred_genres" ADD FOREIGN KEY ("genre_id") REFERENCES "genres" ("id");

ALTER TABLE "connection_search_favorites" ADD FOREIGN KEY ("radio_id") REFERENCES "radios" ("id");

ALTER TABLE "connection_search_favorites" ADD FOREIGN KEY ("connection_id") REFERENCES "connections" ("id");

ALTER TABLE "radio_ad_time" ADD FOREIGN KEY ("radio_id") REFERENCES "radios" ("id");
