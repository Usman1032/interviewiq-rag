export default function RoleSelector({ roles, selectedRole, onSelect }) {
  return (
    <div className="grid gap-3 sm:grid-cols-3">
      {roles.map((role) => {
        const active = role.key === selectedRole;
        return (
          <button
            key={role.key}
            type="button"
            onClick={() => onSelect(role.key)}
            className={`rounded-xl border px-4 py-3 text-left text-sm font-medium transition
              ${
                active
                  ? "border-accent bg-accent/10 text-accent"
                  : "border-black/10 bg-white hover:border-black/30"
              }`}
          >
            {role.label}
          </button>
        );
      })}
    </div>
  );
}
