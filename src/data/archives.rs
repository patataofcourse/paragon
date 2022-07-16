use anyhow::Context;
use linked_hash_map::LinkedHashMap;
use mila::LayeredFilesystem;
use std::collections::HashMap;

pub struct Archives {
    archives: HashMap<String, LinkedHashMap<String, Vec<u8>>>,
    dirty_tracker: HashMap<String, bool>,
}

impl Archives {
    pub fn new() -> Self {
        Archives {
            archives: HashMap::new(),
            dirty_tracker: HashMap::new(),
        }
    }

    pub fn load_file(
        &mut self,
        fs: &LayeredFilesystem,
        archive: &str,
        file_name: &str,
    ) -> anyhow::Result<&[u8]> {
        if !self.archives.contains_key(archive) {
            let arc = fs
                .read_fe9_arc(archive, false)
                .with_context(|| format!("Failed to load CMP archive '{}'", archive))?;
            self.archives.insert(archive.to_string(), arc);
        }
        if let Some(arc) = self.archives.get(archive) {
            if let Some(contents) = arc.get(file_name) {
                Ok(contents)
            } else {
                Err(anyhow::anyhow!(
                    "CMP archive '{}' does not contain file '{}'",
                    archive,
                    file_name
                ))
            }
        } else {
            Err(anyhow::anyhow!(
                "Bad state: CMP archive '{}' is not loaded.",
                archive
            ))
        }
    }

    pub fn overwrite(
        &mut self,
        archive: &str,
        file_name: &str,
        contents: Vec<u8>,
    ) -> anyhow::Result<()> {
        if let Some(arc) = self.archives.get_mut(archive) {
            if !arc.contains_key(file_name) {
                Err(anyhow::anyhow!(
                    "CMP archive '{}' does not contain file '{}'",
                    archive,
                    file_name
                ))
            } else {
                arc.insert(file_name.to_string(), contents);
                self.dirty_tracker.insert(archive.to_string(), true);
                Ok(())
            }
        } else {
            Err(anyhow::anyhow!(
                "Bad state: CMP archive '{}' is not loaded.",
                archive
            ))
        }
    }

    pub fn save(&self, fs: &LayeredFilesystem) -> anyhow::Result<()> {
        for (k, v) in &self.archives {
            let is_dirty = self.dirty_tracker.get(k).unwrap_or(&false);
            if *is_dirty {
                let raw = mila::fe9_arc::serialize(v)
                    .with_context(|| format!("Failed to serialize CMP archive '{}'", k))?;
                fs.write(k, &raw, false)
                    .with_context(|| format!("Failed to write CMP archive '{}'", k))?;
            }
        }
        Ok(())
    }
}