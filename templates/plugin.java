/*
 * Copyright (C) 2014 {{ author_name }} <{{ author_website }}>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
package {{ java_package }};
{% if metrics %}
import java.io.IOException;{% endif %}{% if command_starter %}
import org.bukkit.command.Command;
import org.bukkit.command.CommandSender;{% endif %}{% if listener_starter %}
import org.bukkit.event.Listener;
import org.bukkit.plugin.PluginManager;{% endif %}
import org.bukkit.plugin.java.JavaPlugin;{% if metrics %}
import org.mcstats.MetricsLite;{% endif %}

public class {{ name }}Plugin extends JavaPlugin{% if listener_start %} implements Listener{% endif %} {

    @Override
    public void onEnable() {{% if listener_starter %}
        PluginManager pm = getServer().getPluginManager();
        pm.registerEvents(this, this);{% endif %}{% if metrics %}
        MetricsLite metrics = null;
        try {
            metrics = new MetricsLite(this);
        } catch (IOException ex) {
            // We just won't do metrics
        }
        if (metrics != null) {
            metrics.start();
        }{% endif %}
    }

    @Override
    public void onDisable() {
    }{% if command_starter %}

    @Override
    public boolean onCommand(CommandSender sender, Command cmd, String label, String[] args) {
        sender.sendMessage("{{ name }} doesn't know about the command /" + cmd.getName());
        return true;
    }{% endif %}
}
