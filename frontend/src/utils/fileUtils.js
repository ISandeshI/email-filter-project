export function cleanFilename(filename) {
  if (!filename) return "";

  return filename.includes("_")
    ? filename.split("_").slice(1).join("_")
    : filename;
}