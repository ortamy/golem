-- Схема waitlist для последующего подключения Supabase.
create table if not exists public.waitlist (
  id bigint generated always as identity primary key,
  email text unique not null,
  created_at timestamptz default now()
);

alter table public.waitlist enable row level security;

create policy "waitlist anon insert"
  on public.waitlist
  for insert
  to anon
  with check (char_length(email) > 3);