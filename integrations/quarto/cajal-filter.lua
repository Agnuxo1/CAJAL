-- cajal-filter.lua
-- CAJAL Quarto Extension
-- Adds scientific paper generation capabilities to Quarto documents

-- Paper metadata extraction
function Meta(meta)
  if meta.cajal then
    quarto.log.output("CAJAL: Paper generation enabled")
    
    -- Extract paper configuration
    local paper_config = {
      topic = meta.cajal.topic or meta.title,
      authors = meta.cajal.authors or meta.author,
      keywords = meta.cajal.keywords or {},
      references = meta.cajal.references or 8,
      format = meta.cajal.format or "full_paper"
    }
    
    -- Store for later use
    quarto.doc.cajal_config = paper_config
  end
  return meta
end

-- Process code blocks with cajal class
function CodeBlock(el)
  if el.classes:includes("cajal") then
    -- This is a CAJAL paper generation block
    local content = el.text
    
    -- Mark for post-processing (actual generation happens via Python/R filter)
    return pandoc.Div(
      {pandoc.Para({pandoc.Str("[CAJAL: Generating paper section...]")})},
      {class = "cajal-generating", data_content = content}
    )
  end
  return el
end

-- Add CAJAL CSS class to document
function Pandoc(doc)
  return doc
end
